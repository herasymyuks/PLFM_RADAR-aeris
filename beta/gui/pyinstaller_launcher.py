"""PyInstaller entry script (absolute import; ``python -m aeris10_gui`` is the normal entry)."""
import sys

from aeris10_gui.app import main

if __name__ == "__main__":
    sys.exit(main())
