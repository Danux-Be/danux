#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

try:
    import setproctitle
    setproctitle.setproctitle("Wondershaper QuickToggle")
except ImportError:
    pass

LIB_DIR = Path("/usr/lib/wondershaper-quicktoggle")
if LIB_DIR.exists():
    sys.path.insert(0, str(LIB_DIR))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import main

if __name__ == "__main__":
    raise SystemExit(main())
