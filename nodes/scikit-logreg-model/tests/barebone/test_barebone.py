import os
import fsspec
import subprocess

from tests.utils import CwdContextManager


def call_create(barebone_dir, src, dest, interface="args"):
    fs = fsspec.filesystem("file")
    if fs.exists(dest):
        fs.rm(dest, recursive=True)
    os.makedirs(dest, exist_ok=True)

    with CwdContextManager():
        subprocess.run(
            ["uv", "run", "src/mki_barebone/main.py", "-i", src, "-o", dest, "--interface", interface],
            cwd=barebone_dir,
            check=True,
        )

    return src, dest


def check_filematch(dest, testsrc, files_to_match):
    for relpath in files_to_match:
        testsrcpath = os.path.join(testsrc, relpath)
        destpath = os.path.join(dest, relpath)
        assert os.path.exists(testsrcpath), f"{testsrcpath} does not exist"
        assert os.path.exists(destpath), f"{destpath} does not exist"
        with open(testsrcpath) as f1:
            with open(destpath) as f2:
                assert (
                    f1.read().strip() == f2.read().strip()
                ), f"files for {relpath} do not match"
