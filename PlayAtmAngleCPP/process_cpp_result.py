from __future__ import annotations

import sys
from pathlib import Path


current_folder = Path(__file__).resolve().parent
project_root = current_folder.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ImageProcessv2.services.atomization_result_export_service import (  # noqa: E402
    AtomizationResultExportService,
    load_legacy_input,
)


def main() -> None:
    config = load_legacy_input(
        current_folder / "inputpy.txt",
        current_folder / "result.csv",
        open_workbooks=True,
    )
    AtomizationResultExportService().export_from_csv(config)
    print("雾化锥角后处理完成")


if __name__ == "__main__":
    main()
