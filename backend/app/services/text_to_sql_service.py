from supabase import Client
from app.services.llm_providers import get_llm_provider
import re
import logging

logger = logging.getLogger(__name__)


class TextToSQLService:
    """
    Converts natural language queries to SQL and executes them against documents table.
    """

    # SQL template for document statistics queries
    SQL_SCHEMA = """
Table: documents
Columns:
- id (UUID)
- user_id (UUID)
- filename (TEXT)
- file_path (TEXT)
- file_size (INTEGER) - in bytes
- mime_type (TEXT)
- status (TEXT) - 'pending', 'processing', 'completed', 'failed'
- chunk_count (INTEGER)
- metadata (JSONB) - contains title, author, category, tags, summary, language
- created_at (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)
"""

    SYSTEM_PROMPT = f"""You are a SQL expert. Convert the user's natural language question into a safe SQL query.

Rules:
1. Only generate SELECT statements - NO INSERT, UPDATE, DELETE, or DROP
2. Only query the 'documents' table
3. Always filter by user_id for RLS compliance: WHERE user_id = '{'{user_id}'}'
4. Use proper SQL syntax
5. Return just the SQL query, no explanation

{SQL_SCHEMA}

Example queries:
- "How many documents do I have?" -> SELECT COUNT(*) FROM documents WHERE user_id = '{{user_id}}'
- "What is my total file size?" -> SELECT COALESCE(SUM(file_size), 0) FROM documents WHERE user_id = '{{user_id}}'
- "Show me document sizes" -> SELECT filename, file_size FROM documents WHERE user_id = '{{user_id}}' ORDER BY file_size DESC
"""

    def __init__(self, supabase: Client, provider_type: str = "minimax"):
        self.supabase = supabase
        self.llm_provider = get_llm_provider(provider_type)

    async def generate_and_execute(self, query: str, user_id: str) -> dict:
        """
        1. Use LLM to convert natural language to SQL
        2. Validate SQL safety (SELECT only, documents table only)
        3. Execute SQL
        4. Return results
        """
        # Generate SQL
        sql = await self._generate_sql(query, user_id)
        if sql.get("error"):
            return sql

        # Validate
        if not self._is_safe_sql(sql["query"]):
            return {"error": "Unsafe SQL query detected. Only SELECT queries are allowed."}

        # Execute
        return await self._execute_sql(sql["query"], user_id)

    async def _generate_sql(self, query: str, user_id: str) -> dict:
        """Use LLM to generate SQL from natural language query."""
        try:
            # Replace placeholder with actual user_id
            system_msg = self.SYSTEM_PROMPT.replace("{user_id}", user_id)

            response = await self.llm_provider.chat_complete(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"Convert this question to SQL: {query}"}
                ],
                stream=False
            )

            # Extract SQL from response
            sql_query = self._extract_sql(response)
            if not sql_query:
                return {"error": "Failed to generate SQL query"}

            logger.info(f"Generated SQL: {sql_query}")
            return {"query": sql_query}

        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return {"error": str(e)}

    def _extract_sql(self, response: str) -> str:
        """Extract SQL query from LLM response."""
        # Remove markdown code blocks if present
        if "```" in response:
            # Find the SQL between ``` and ```
            match = re.search(r'```(?:sql)?\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Remove common prefixes
        response = response.strip()
        if response.upper().startswith("SQL:"):
            response = response[4:].strip()

        return response

    def _is_safe_sql(self, sql: str) -> bool:
        """
        Validate SQL is safe (SELECT only, documents table only).
        """
        sql_upper = sql.upper().strip()

        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            return False

        # Block dangerous keywords
        dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE"]
        for keyword in dangerous:
            if keyword in sql_upper:
                # Check if it's a column name containing the keyword (false positive)
                # Only block if it's a statement keyword
                pattern = r'\b' + keyword + r'\b'
                if re.search(pattern, sql_upper):
                    return False

        # Must only reference documents table
        # Extract table references
        from_match = re.search(r'\bFROM\s+(\w+)', sql_upper)
        if from_match:
            table = from_match.group(1).lower()
            if table != 'documents':
                return False

        return True

    async def _execute_sql(self, sql: str, user_id: str) -> dict:
        """Execute SQL query and return formatted results."""
        try:
            # Replace placeholder with actual user_id
            sql = sql.replace("{user_id}", user_id)

            # Execute via Supabase
            response = self.supabase.rpc("exec_sql", {"query": sql}).execute()

            if response.data is None:
                # Try direct query if RPC doesn't exist
                return {"error": "SQL execution not available via RPC"}

            return {
                "type": "text_to_sql",
                "query": sql,
                "results": response.data,
                "row_count": len(response.data) if response.data else 0
            }

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return {"error": f"SQL execution failed: {str(e)}"}

    def format_results(self, results: dict) -> str:
        """Format SQL results as a readable string."""
        if results.get("error"):
            return f"Error: {results['error']}"

        data = results.get("results", [])
        if not data:
            return "No results found."

        # Format as table
        if isinstance(data, list) and len(data) > 0:
            # Get column names
            columns = list(data[0].keys())
            header = " | ".join(columns)
            separator = "-" * len(header)

            rows = []
            for row in data[:10]:  # Limit to 10 rows
                values = [str(row.get(col, "")) for col in columns]
                rows.append(" | ".join(values))

            result_str = f"**Query Results ({results.get('row_count', len(data))} rows)**\n\n"
            result_str += f"{header}\n{separator}\n" + "\n".join(rows)

            if len(data) > 10:
                result_str += f"\n... and {len(data) - 10} more rows"

            return result_str

        return str(data)
