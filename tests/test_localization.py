import sys
import tkinter as tk
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from AtmProcess.application.app_state import AppState
from AtmProcess.domain.settings import AppSettings
from AtmProcess.ui import localized_dialogs, localized_widgets as ttk
from AtmProcess.ui.localization import language_for, translate


class TranslationTests(unittest.TestCase):
    def test_default_and_unknown_text_are_unchanged(self):
        self.assertEqual(translate("液膜测量"), "液膜测量")
        self.assertEqual(translate("液膜测量", "en"), "Liquid sheet")
        self.assertEqual(translate("unregistered message", "en"), "unregistered message")

    def test_dynamic_paths_and_numbers_stay_literal(self):
        path = r"E:\实验数据\平均图\实验编号24_预览图.tif"
        self.assertEqual(translate(f"计算平均图 完成：{path}", "en"), f"Compute average image completed: {path}")
        self.assertEqual(translate("已导出：平均图.xlsx", "en"), "Exported: 平均图.xlsx")
        self.assertEqual(
            translate("已记录 20 点；破碎长度平均值：4.6 mm；标准差：0.32 mm", "en"),
            "Recorded: 20; mean breakup length: 4.6 mm; SD: 0.32 mm",
        )
        self.assertEqual(translate("1/20（5.0%）", "en"), "1/20 (5.0%)")

    def test_hover_and_error_fragments_are_translated(self):
        self.assertEqual(
            translate("坐标：x=-2, y=1050，灰度：图像外，模式：breakup", "en"),
            "Position: x=-2, y=1050; gray: Outside image; mode: breakup",
        )
        self.assertEqual(
            translate("雾化锥角批处理 失败：图像帧率必须大于 0", "en"),
            "Spray-angle batch failed: Image frame rate must be greater than 0",
        )

    def test_language_persists_and_older_settings_default_to_chinese(self):
        self.assertEqual(AppSettings.from_dict({}).language, "zh")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            state = AppState(path)
            state.settings.language = "en"
            state.settings.active_page = "雾化锥角"
            state.save()
            restored = AppState(path).settings
            self.assertEqual(restored.language, "en")
            self.assertEqual(restored.active_page, "雾化锥角")


class LocalizedWidgetTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.language = language_for(self.root)

    def test_bound_text_changes_without_writing_source_variables(self):
        source = tk.StringVar(self.root, value="播放")
        on_write = Mock()
        source.trace_add("write", on_write)
        label = ttk.Label(self.root, textvariable=source)
        entry = ttk.Entry(self.root, textvariable=source)
        literal = ttk.Label(self.root, textvariable=source, translate=False)
        self.language.set_language("en")
        self.assertEqual(label["text"], "Play")
        self.assertEqual(source.get(), "播放")
        self.assertEqual(entry.get(), "播放")
        self.assertEqual(literal["text"], "播放")
        on_write.assert_not_called()
        source.set("暂停")
        self.assertEqual(label["text"], "Pause")
        self.language.set_language("zh")
        self.assertEqual(label["text"], "暂停")
        label.destroy()
        source.set("播放")  # Destroyed widgets must release their variable traces.

    def test_tabs_and_table_translate_without_changing_identifiers_or_rows(self):
        notebook = ttk.Notebook(self.root)
        page = ttk.Frame(notebook)
        notebook.add(page, text="液膜测量")
        table = ttk.Treeview(page, columns=("帧数", "左线"), show="headings")
        table.heading("帧数", text="帧数")
        table.heading("左线", text="左线")
        row = table.insert("", "end", values=(24, 60))
        selected = notebook.select()
        values = table.item(row, "values")
        self.language.set_language("en")
        self.assertEqual(notebook.tab(page, "text"), "Liquid sheet")
        self.assertEqual(notebook.select(), selected)
        self.assertEqual(table.heading("帧数", "text"), "Frame")
        self.assertEqual(table["columns"], ("帧数", "左线"))
        self.assertEqual(table.item(row, "values"), values)
        table.configure(columns=("帧数", "破碎线"))
        table.heading("破碎线", text="破碎线")
        self.assertEqual(table.heading("破碎线", "text"), "Breakup y")
        self.language.set_language("zh")  # Previous mode's absent columns must not interrupt translation.
        self.assertEqual(table.heading("破碎线", "text"), "破碎线")
        self.language.set_language("en")
        self.assertEqual(ttk.Button(self.root, text="浏览")["text"], "Browse")

    def test_dialog_translates_labels_only(self):
        self.language.set_language("en")
        path = r"E:\实验数据\平均图.xlsx"
        with patch.object(localized_dialogs._files, "askopenfilename", return_value=path) as choose:
            selected = localized_dialogs.askopenfilename(
                parent=self.root,
                title="选择汇总表",
                initialdir=r"E:\实验数据",
                initialfile="平均图.xlsx",
                filetypes=[("Excel 表格", "*.xlsx")],
            )
        self.assertEqual(selected, path)
        self.assertEqual(choose.call_args.kwargs["title"], "Select summary workbook")
        self.assertEqual(choose.call_args.kwargs["initialdir"], r"E:\实验数据")
        self.assertEqual(choose.call_args.kwargs["initialfile"], "平均图.xlsx")
        self.assertEqual(choose.call_args.kwargs["filetypes"], [("Excel workbooks", "*.xlsx")])

    def test_app_toggle_preserves_processing_state_and_pending_entries(self):
        from AtmProcess.ui.app_window import AppWindow

        with TemporaryDirectory() as directory:
            state = AppState(Path(directory) / "settings.json")
            state.experiment.data_root = Path(directory)
            with patch("AtmProcess.ui.preview.image_preview_pane.read_image", return_value=np.zeros((8, 8), dtype=np.uint8)):
                app = AppWindow(self.root, state)
                self.root.update()
            self.addCleanup(app.destroy)
            app.experiment_panel.experiment_no.set(24)  # Deliberately not committed with Enter.
            measurement = app.pages.pages[0]
            measurement.sheet_records.append(["1", 1, 2, 4, 3, 6, 2, 0.02, 3, 0.03])
            measurement._refresh_table()
            profile = app.pages.pages[3].profile_panel
            data = {title: (np.array([0., 1.]), np.array([2., 3.]), 0.5) for title in profile.titles}
            profile.update_data(data)
            self.root.update()
            before = state.settings.to_dict()
            selected = app.pages.select()
            rows = measurement.table.get_children()
            limits = [(axis.get_xlim(), axis.get_ylim()) for axis in profile.axes]
            artist_data = profile.artists["左侧原始"][0].get_ydata().copy()
            cache = app.pages.pages[3]._sampling_geometry
            with patch.object(app.preview, "refresh") as refresh, patch.object(app.experiment_panel, "apply_to_state") as apply:
                app.experiment_panel._toggle_language()
                self.root.update()
                self.assertEqual(profile.axes[0].get_title(), "Left: raw")
                self.assertEqual(profile.axes[0].get_xlabel(), "Angle/deg")
                self.assertEqual(state.settings.to_dict(), {**before, "language": "en"})
                app.experiment_panel._toggle_language()
                self.root.update()
                self.assertEqual(profile.axes[0].get_title(), "左侧原始")
                refresh.assert_not_called()
                apply.assert_not_called()
            self.assertEqual(state.settings.to_dict(), before)
            self.assertEqual(app.experiment_panel.experiment_no.get(), 24)
            self.assertEqual(app.pages.select(), selected)
            self.assertEqual(measurement.table.get_children(), rows)
            self.assertEqual([(axis.get_xlim(), axis.get_ylim()) for axis in profile.axes], limits)
            np.testing.assert_array_equal(profile.artists["左侧原始"][0].get_ydata(), artist_data)
            self.assertIs(app.pages.pages[3]._sampling_geometry, cache)


if __name__ == "__main__":
    unittest.main()
