import os
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

try:
    import streamlit as st
except Exception:
    st = None

SENSITIVE_HEADER_KEYS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "api-key",
    "token",
}

SENSITIVE_JSON_KEYS = {
    "token",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "authorization",
    "api_key",
    "key",
}


class SessionFilter(logging.Filter):
    def filter(self, record):
        session_id = "Unknown"
        if st is not None:
            try:
                session_id = st.session_state.get("session_id", "Unknown")
            except Exception:
                pass
        record.session_id = session_id
        return True


def truncate_text(value, max_len=500):
    if value is None:
        return ""
    text = str(value)
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}... [truncated {len(text) - max_len} chars]"


def sanitize_headers(headers):
    safe = {}
    for k, v in dict(headers).items():
        if str(k).lower() in SENSITIVE_HEADER_KEYS:
            safe[k] = "[REDACTED]"
        else:
            safe[k] = truncate_text(v, 200)
    return safe


def sanitize_json(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if str(k).lower() in SENSITIVE_JSON_KEYS:
                out[k] = "[REDACTED]"
            else:
                out[k] = sanitize_json(v)
        return out
    if isinstance(obj, list):
        return [sanitize_json(x) for x in obj]
    if isinstance(obj, str):
        return truncate_text(obj, 500)
    return obj


def safe_response_preview(response, max_len=500):
    ctype = str(response.headers.get("Content-Type", "")).lower()
    if "application/json" in ctype:
        try:
            parsed = response.json()
            safe = sanitize_json(parsed)
            text = json.dumps(safe, ensure_ascii=True)
            return truncate_text(text, max_len)
        except Exception:
            pass
    return truncate_text(response.text, max_len)


def configure_logging(level=None):
    logger = logging.getLogger("gfs")

    # Idempotent setup: avoid duplicate handlers on Streamlit reruns.
    if logger.handlers:
        return logger

    if level is None:
        level = getattr(logging, os.getenv("GFS_LOG_LEVEL", "DEBUG").upper(), logging.DEBUG)

    logger.setLevel(level)
    logger.propagate = False

    log_dir = Path(os.getenv("GFS_LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s [session=%(session_id)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    session_filter = SessionFilter()
    file_handler.addFilter(session_filter)
    stream_handler.addFilter(session_filter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def get_logger(name):
    base = configure_logging()
    return base.getChild(name)

# Functions to both log and show user facing errors
def log_and_show(message, exc_info=False, level=logging.ERROR):
    """Log a page-level error once and show it to the user via st.error.

    Pass exc_info=True inside an `except` block to capture the traceback.
    """
    base = configure_logging()
    base.getChild("pages").log(level, message, exc_info=exc_info)
    if st is not None:
        try:
            st.error(message)
        except Exception:
            pass


def log_and_warn(message):
    """Log a page-level warning once and show it to the user via st.warning."""
    base = configure_logging()
    base.getChild("pages").warning(message)
    if st is not None:
        try:
            st.warning(message)
        except Exception:
            pass