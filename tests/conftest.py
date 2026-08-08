"""Session-wide test isolation from the developer's local ql.toml.

quake_loyola.config resolves ``CONFIG_PATH`` (and several constants modules
freeze ``config.get()``/``config.get_build()`` values) from the repo root at
*import time* — the first time anything imports ``quake_loyola`` in this
process. If a developer has a local, gitignored ``ql.toml`` with overridden
flags/build settings, tests that assert default-config behavior (e.g.
``config.get_build("sky") == "sky4"``, the regression suite's golden
brush/entity counts and MD5 hash) would spuriously fail — not because the
code is broken, but because the ambient config changed the generated output.

To guarantee every test sees the hardcoded defaults regardless of the
developer's ql.toml, chdir into an empty temporary directory *before*
``quake_loyola`` (and therefore ``quake_loyola.config``) is ever imported.
``quake_loyola.config._find_repo_root`` walks upward from cwd looking for
``pyproject.toml``/``.git`` and falls back to cwd itself when neither is
found, so an isolated empty tmp directory (outside the repo tree) resolves
to a REPO_ROOT with no ql.toml — i.e. every flag/build setting is exactly
its hardcoded default for the whole test session.
"""

from __future__ import annotations

import os
import tempfile

_original_cwd: str | None = None
_tmp_dir: tempfile.TemporaryDirectory[str] | None = None


def pytest_configure(config):  # noqa: ARG001 - pytest hook signature
    global _original_cwd, _tmp_dir
    _original_cwd = os.getcwd()
    _tmp_dir = tempfile.TemporaryDirectory(prefix="quake-loyola-test-config-")
    os.chdir(_tmp_dir.name)


def pytest_unconfigure(config):  # noqa: ARG001 - pytest hook signature
    global _original_cwd, _tmp_dir
    if _original_cwd is not None:
        os.chdir(_original_cwd)
        _original_cwd = None
    if _tmp_dir is not None:
        _tmp_dir.cleanup()
        _tmp_dir = None
