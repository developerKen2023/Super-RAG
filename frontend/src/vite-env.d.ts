/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string
  readonly VITE_SUPABASE_ANON_KEY: string
  readonly VITE_API_URL: string
  readonly VITE_LANGSMITH_API_KEY: string
  readonly VITE_LANGSMITH_PROJECT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
