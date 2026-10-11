import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class IndependenceTests(unittest.TestCase):
    def run_isolated(self, code: str) -> None:
        with TemporaryDirectory() as working_directory:
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-c", code, str(PROJECT_ROOT)],
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=60,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_modules_and_settings_resolve_inside_project(self):
        self.run_isolated('''
import importlib
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root.parent))
for source in root.rglob("*.py"):
    relative = source.relative_to(root)
    if relative.parts[0] == "tests":
        continue
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    name = ".".join(["AtmProcess", *parts])
    module = importlib.import_module(name)
    assert Path(module.__file__).resolve() == source.resolve(), name

from AtmProcess.application.app_state import AppState
assert AppState().settings_store.path == root / "settings.json"
''')

    def test_script_and_module_entry_points_initialize_without_gui(self):
        for module_mode in (False, True):
            with self.subTest(module_mode=module_mode):
                self.run_isolated('''
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[1])
sys.path.insert(0, str(root.parent))
with patch("tkinter.Tk") as create_root, patch("AtmProcess.ui.app_window.AppWindow") as create_app:
    if MODULE_MODE:
        runpy.run_module("AtmProcess.main", run_name="__main__")
    else:
        sys.path.remove(str(root.parent))  # Direct launch must find its own package.
        runpy.run_path(str(root / "main.py"), run_name="__main__")
    window = create_root.return_value
    window.title.assert_called_once_with("AtmProcess")
    window.mainloop.assert_called_once_with()
    create_app.assert_called_once()
    close_window = window.protocol.call_args.args[1]
    close_window()
    create_app.return_value.save.assert_called_once_with()
    window.destroy.assert_called_once_with()
'''.replace("MODULE_MODE", repr(module_mode)))

    def test_atomization_workers_keep_frame_order_and_results(self):
        self.run_isolated('''
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root.parent))
import numpy as np
from AtmProcess.algorithms.atomization import (
    AtomizationParameters, _calculate_atomization_chunk, calculate_atomization_batch,
)

folder = root / "sample_data" / "atomization" / "实验编号55"
frames = [6800, 6802, 6804]
parameters = AtomizationParameters(267, 312, 107, 250, 0, 1800, 100, 0, 100, 0, 0.85, 0.8, 101, 1)
expected = np.asarray(_calculate_atomization_chunk((folder, frames, parameters, False)))
progress = []
actual = calculate_atomization_batch(
    folder, frames, 2, parameters, progress_callback=lambda done, total: progress.append((done, total)),
)
np.testing.assert_array_equal(actual[:, 0], frames)
np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-9)
assert np.isfinite(actual).all()
assert progress[0] == (0, len(frames))
assert progress[-1] == (len(frames), len(frames))
''')


if __name__ == "__main__":
    unittest.main()
