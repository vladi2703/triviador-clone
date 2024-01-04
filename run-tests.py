import sys
import pytest

if __name__ == "__main__":
    exit_code = pytest.main(["./test"])
    sys.exit(exit_code)
