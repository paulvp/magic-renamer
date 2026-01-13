#!/bin/bash


# Wrapper to run MagicRenamer GUI with proper environment
export QT_XCB_GL_INTEGRATION=none
export LIBGL_ALWAYS_SOFTWARE=1
export GDK_SYNCHRONIZE=1

# Try system Python first, fall back to uv
if command -v python3 &> /dev/null && python3 -c "import tkinter" 2>/dev/null; then
    python3 magicrenamer_gui.py "$@"
else
    uv run magicrenamer_gui.py "$@"
fi
