from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable


class ExcelWorkbookError(RuntimeError):
    """目标工作簿无法安全准备或写入时抛出。"""


class ExcelWorkbookCoordinator:
    """协调单个目标工作簿，不修改任何无关的 Excel 工作簿。"""

    def __init__(
        self,
        active_excel_provider: Callable[[], Any | None] | None = None,
        file_opener: Callable[[Path], None] | None = None,
        close_wait_seconds: float = 0.15,
    ) -> None:
        self._active_excel_provider = active_excel_provider or self._get_active_excel
        self._file_opener = file_opener or self._open_with_default_application
        self._close_wait_seconds = close_wait_seconds

    def close_if_open(self, path: str | Path) -> Path:
        """仅保存并关闭完整路径与 *path* 一致的 Excel 工作簿。"""
        target = Path(path)
        matching_workbooks = self._find_matching_workbooks(target)
        for workbook in matching_workbooks:
            try:
                workbook.Save()
                workbook.Close(True)  # Excel COM 动态接口只接受位置参数；True 表示保存更改。
            except Exception as error:
                raise ExcelWorkbookError(f"无法保存并关闭已打开的目标工作簿：{target}") from error

        if matching_workbooks and self._close_wait_seconds:
            time.sleep(self._close_wait_seconds)  # 等待 Excel 释放文件锁。
        return target

    def save_and_open(self, workbook: Any, path: str | Path) -> Path:
        """写入 openpyxl 工作簿后，自动打开写入完成的目标文件。"""
        target = self.close_if_open(path)
        try:
            workbook.save(target)
        except PermissionError:
            # 首次检查后目标文件可能又被打开，再按完整路径关闭一次匹配工作簿。
            self.close_if_open(target)
            try:
                workbook.save(target)
            except PermissionError as retry_error:
                raise ExcelWorkbookError(
                    f"无法写入 Excel 文件：{target}。请确认该文件没有被 WPS 或其他程序占用。"
                ) from retry_error

        try:
            self._file_opener(target)
        except OSError as error:
            raise ExcelWorkbookError(f"Excel 文件已写入，但无法自动打开：{target}") from error
        return target

    def _find_matching_workbooks(self, target: Path) -> list[Any]:
        excel = self._active_excel_provider()
        if excel is None:
            return []

        try:
            workbooks = excel.Workbooks
            count = int(workbooks.Count)
            target_path = self._normalize_path(target)
            matches = []
            for index in range(1, count + 1):
                workbook = workbooks.Item(index)
                if self._normalize_path(workbook.FullName) == target_path:
                    matches.append(workbook)
            return matches
        except ExcelWorkbookError:
            raise
        except Exception as error:
            raise ExcelWorkbookError(f"无法检查已打开的 Excel 工作簿：{target}") from error

    def _get_active_excel(self) -> Any | None:
        try:
            import comtypes.client

            return comtypes.client.GetActiveObject("Excel.Application", dynamic=True)
        except (ImportError, OSError):
            return None  # Excel 未运行，或当前 Python 缺少 COM 依赖。

    @staticmethod
    def _normalize_path(path: str | Path) -> str:
        return os.path.normcase(os.path.abspath(os.path.realpath(os.fspath(path))))

    @staticmethod
    def _open_with_default_application(path: Path) -> None:
        os.startfile(str(path))
