import subprocess
import test_helpers
import pytest
import os

CONST = test_helpers.yaml_loader()

@pytest.fixture(autouse=True,scope="session")
def start_conn():
    s = subprocess.Popen([CONST["CONNECTION_APP"], f"{os.path.join(os.getcwd(), CONST["CONNECTION_APP_ARGS"])}"])
    yield
    s.kill()


