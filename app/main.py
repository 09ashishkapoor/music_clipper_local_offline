import os
import sys
import tkinter

# Monkeypatch for Python 3.14+ compatibility with tkinterdnd2
# tkinter.tix was removed in Python 3.14, but tkinterdnd2 still tries to import and use it.
if not hasattr(tkinter, 'tix'):
    class MockTix:
        Tk = tkinter.Tk
        TixWidget = object
    sys.modules['tkinter.tix'] = MockTix
    tkinter.tix = MockTix

from tkinterdnd2 import TkinterDnD
from ui import SongClipperApp

# Ensure app directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    root = TkinterDnD.Tk()
    app = SongClipperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
