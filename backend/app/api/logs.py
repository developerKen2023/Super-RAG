from fastapi import APIRouter, Depends
from pydantic import BaseModel
import logging
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)


class LogEntry(BaseModel):
    level: str
    message: str
    source: str = "frontend"


@router.post("/logs")
async def write_log(entry: LogEntry):
    """Receive and write logs from frontend."""
    log_dir = Path(__file__).parent.parent.parent.parent / "log"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "frontend.log"

    log_level = getattr(logging, entry.level.upper(), logging.INFO)
    logger.log(log_level, f"[{entry.source}] {entry.message}")

    # Also write directly to file
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{entry.level.upper()}] [{entry.source}] {entry.message}\n")

    return {"status": "ok"}
