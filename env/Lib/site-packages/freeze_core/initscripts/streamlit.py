"""Initialization script for streamlit app built with cx_Freeze."""

from __future__ import annotations

import os
import sys
from importlib import import_module
from tempfile import TemporaryDirectory

sys.frozen = True


def run(name) -> None:
    """Execute the main script of the streamlit frozen application."""
    cli = import_module("streamlit.web.cli")
    with TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "streamlit_app.py"), "w+") as f:
            f.write(f"import {name}\n")
        sys.argv[1:1] = ["run", tmpdir, "--global.developmentMode=false"]
        sys.exit(cli.main())
