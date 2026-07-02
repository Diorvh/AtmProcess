from __future__ import annotations

import subprocess
from pathlib import Path

from core.atomization_angle_runner import AtomizationAngleBatchConfig, AtomizationAngleCppRunner


class AtomizationAngleService:
    def __init__(self, cpp_dir: str | Path) -> None:
        self.runner = AtomizationAngleCppRunner(cpp_dir)

    def run_batch(self, config: AtomizationAngleBatchConfig) -> subprocess.CompletedProcess:
        return self.runner.run_batch(config)
