import json
import shutil
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from AtmProcess.application.app_state import AppState
from AtmProcess.core.config import SettingsStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SettingsStoreTests(unittest.TestCase):
    def prepare_example(self, root):
        shutil.copy2(PROJECT_ROOT / "settings.example.json", root / "settings.example.json")
        (root / "sample_data").mkdir()
        template = Path("sample_data/atomization_summary_template.xlsx")
        shutil.copy2(PROJECT_ROOT / template, root / template)

    def test_fresh_install_loads_atomization_sample(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare_example(root)
            state = AppState(root / "settings.json")
            self.assertEqual(state.settings.active_page, "雾化锥角")
            self.assertEqual(state.experiment.image_folder, root / "sample_data/atomization/实验编号29")
            self.assertEqual(state.experiment.frames.frame_numbers(), list(range(8000, 8020)))
            self.assertEqual(state.experiment.frames.current, 8000)
            self.assertEqual(state.settings.atomization.thres_ratio_left, 0.5)
            self.assertEqual(state.settings.atomization.thres_ratio_right, 0.5)
            self.assertEqual(state.settings.atomization.x_left, 277)
            self.assertEqual(state.settings.atomization.x_right, 302)
            summary = root / "sample_data/results/atomization_summary.xlsx"
            self.assertEqual(state.experiment.result_summary, summary)
            self.assertEqual(summary.read_bytes(), (root / "sample_data/atomization_summary_template.xlsx").read_bytes())
            self.assertFalse((root / "settings.json").exists())

    def test_first_run_does_not_overwrite_existing_sample_results(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare_example(root)
            summary = root / "sample_data/results/atomization_summary.xlsx"
            summary.parent.mkdir()
            summary.write_bytes(b"previous result")
            (root / "settings.json").touch()
            AppState(root / "settings.json")
            self.assertEqual(summary.read_bytes(), b"previous result")

    def test_personal_settings_take_precedence_without_merging_sample(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(PROJECT_ROOT / "settings.example.json", root / "settings.example.json")
            data = {"language": "en", "experiment": {"experiment_no": 56}, "active_page": "液膜测量"}
            path = root / "settings.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(SettingsStore(path).load(), data)
            state = AppState(path)
            self.assertIsNone(state.experiment.result_summary)
            self.assertFalse((root / "sample_data/results").exists())

    def test_paths_remain_portable_after_save_and_relocation(self):
        with TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            first.mkdir()
            second.mkdir()
            external = Path(directory) / "external.xlsx"
            data = {
                "experiment": {"data_root": str(first / "sample_data/atomization"),
                               "result_summary": str(external), "direct_image": ""},
                "atomization": {"export_dir": str(first / "sample_data/results")},
                "preview": {"save_dir": str(first / "sample_data/results/preview"), "filename": "8000.tif"},
                "measurement": {"export_dir": ""},
            }
            SettingsStore(first / "settings.json").save(data)
            self.assertEqual(data["experiment"]["data_root"], str(first / "sample_data/atomization"))
            serialized = json.loads((first / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(serialized["experiment"]["data_root"], "sample_data/atomization")
            shutil.copy2(first / "settings.json", second / "settings.json")
            restored = SettingsStore(second / "settings.json").load()
            self.assertEqual(restored["experiment"]["data_root"], str(second / "sample_data/atomization"))
            self.assertEqual(restored["atomization"]["export_dir"], str(second / "sample_data/results"))
            self.assertEqual(restored["preview"]["save_dir"], str(second / "sample_data/results/preview"))
            self.assertEqual(restored["experiment"]["result_summary"], str(external))
            self.assertEqual(restored["experiment"]["direct_image"], "")
            self.assertEqual(restored["measurement"]["export_dir"], "")
            self.assertEqual(restored["preview"]["filename"], "8000.tif")

    def test_missing_files_keep_empty_settings_behavior(self):
        with TemporaryDirectory() as directory:
            self.assertEqual(SettingsStore(Path(directory) / "settings.json").load(), {})


if __name__ == "__main__":
    unittest.main()
