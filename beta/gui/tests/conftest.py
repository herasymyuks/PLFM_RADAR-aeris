import os
import sys
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPO = ROOT.parents[1]
ORIGINAL_GUI_DIR = REPO / "9_Firmware" / "9_3_GUI"


@pytest.fixture(scope="session")
def test_csv_path():
    p = ORIGINAL_GUI_DIR / "test_radar_data.csv"
    if not p.exists():
        pytest.skip("test_radar_data.csv not present")
    return p


def tk_available() -> bool:
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False
