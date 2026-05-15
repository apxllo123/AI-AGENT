#!/usr/bin/env python3
"""CLI helper for generating one reply from the Python service code.

Usage:
    python server/reply.py "hello"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_SERVICE = ROOT / "python-service"
sys.path.insert(0, str(PY_SERVICE))
sys.path.insert(0, str(ROOT))

from app import agent_reply  # noqa: E402


def main():
    message = " ".join(sys.argv[1:]).strip() or "hello"
    result = agent_reply(message)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
