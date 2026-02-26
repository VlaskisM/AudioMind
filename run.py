import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent


def run_data_ingress():
    subprocess.run(
        [sys.executable, "run.py"],
        cwd=BASE_DIR / "data_ingress",
    )


if __name__ == "__main__":
    run_data_ingress()
