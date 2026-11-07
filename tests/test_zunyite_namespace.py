# Copyright 2026 Sergii V.Bulavka
# SPDX-License-Identifier: Apache-2.0

"""New canonical GUI Python imports preserve the existing runtime API."""

from pathlib import Path
import tomllib

import pynix_gui
import zunyite_gui
from pynix_gui.backends import default_backend as legacy_backend
from zunyite_gui.backends import default_backend
from pynix_gui.layout import GUIRect as LegacyGUIRect
from zunyite_gui.layout import GUIRect


def test_zunyite_namespace_exports_same_public_runtime():
    assert zunyite_gui.__version__ == pynix_gui.__version__
    assert zunyite_gui.GUIRuntime is pynix_gui.GUIRuntime
    assert zunyite_gui.GUIWindow is pynix_gui.GUIWindow
    assert zunyite_gui.__all__ == pynix_gui.__all__
    assert default_backend is legacy_backend
    assert GUIRect is LegacyGUIRect


def test_zunyite_distribution_declares_both_namespaces():
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert metadata["project"]["name"] == "zunyite-gui"
    include = metadata["tool"]["setuptools"]["packages"]["find"]["include"]
    assert "pynix_gui*" in include
    assert "zunyite_gui*" in include
    assert Path(zunyite_gui.__file__).with_name("py.typed").is_file()


def test_zunyite_owns_pure_text_implementation_without_class_duplication():
    import pynix_gui.text_metrics as legacy_metrics
    import zunyite_gui.text_metrics as canonical_metrics
    import pynix_gui.wrap_engine as legacy_wrap
    import zunyite_gui.wrap_engine as canonical_wrap

    assert canonical_metrics.GUITextExtent is legacy_metrics.GUITextExtent
    assert canonical_metrics.GUITextMetrics is legacy_metrics.GUITextMetrics
    assert canonical_metrics.snapshot_text_metrics is legacy_metrics.snapshot_text_metrics
    assert canonical_metrics.GUITextExtent.__module__ == "zunyite_gui.text_metrics"
    assert canonical_wrap.GUIWrappedText is legacy_wrap.GUIWrappedText
    assert canonical_wrap.wrap_text is legacy_wrap.wrap_text
    assert canonical_wrap.GUIWrappedText.__module__ == "zunyite_gui.wrap_engine"

    # Legacy class/function identity is important for isinstance, pickling,
    # platform backend imports, and compatibility with existing applications.
    wrapped = legacy_wrap.wrap_text(
        "Zunyite GUI", 90,
        measure_width=lambda value: len(value) * 5.0,
        line_height=14,
    )
    assert isinstance(wrapped, canonical_wrap.GUIWrappedText)
    assert wrapped.lines == ("Zunyite GUI",)


def test_canonical_ide_bridges_reuse_existing_service_types_and_functions():
    from zunyite_gui.ide_workspace_session import WorkspaceSession as CanonicalSession
    from pynix_gui.ide_workspace_session import WorkspaceSession as LegacySession
    from zunyite_gui.ide_core_persistent import PersistentCoreReader as CanonicalCore
    from pynix_gui.ide_core_persistent import PersistentCoreReader as LegacyCore
    from zunyite_gui.ide_project_runner import ProjectRunner as CanonicalRunner
    from pynix_gui.ide_project_runner import ProjectRunner as LegacyRunner
    from zunyite_gui.ide_debug_process_client import DebugProcessClient as CanonicalDebug
    from pynix_gui.ide_debug_process_client import DebugProcessClient as LegacyDebug
    from zunyite_gui.ide_workspace_preview import attach_workspace as canonical_attach
    from pynix_gui.ide_workspace_preview import attach_workspace as legacy_attach

    assert CanonicalSession is LegacySession
    assert CanonicalSession.__module__ == "zunyite_gui.ide_workspace_session"
    assert CanonicalCore is LegacyCore
    assert CanonicalCore.__module__ == "zunyite_gui.ide_core_persistent"
    assert CanonicalRunner is LegacyRunner
    assert CanonicalRunner.__module__ == "zunyite_gui.ide_project_runner"
    assert CanonicalDebug is LegacyDebug
    assert canonical_attach is legacy_attach


def test_first_party_public_examples_use_canonical_gui_imports():
    examples = Path(__file__).resolve().parents[1] / "examples"
    for filename in (
        "adv_01_commands_smoke.py",
        "adv_02_tree_table_smoke.py",
        "adv_03_drag_dock_smoke.py",
        "adv_04_canvas_smoke.py",
        "adv_05_editor_smoke.py",
        "macos_smoke.py",
        "resources_smoke.py",
        "text_wrap_smoke.py",
        "showcase.py",
        "real_project_app.py",
    ):
        code = (examples / filename).read_text(encoding="utf-8")
        assert "from zunyite_gui import" in code, filename
        assert "from pynix_gui import" not in code, filename


def test_native_workspace_entrypoint_routes_core_run_debug_through_canonical_paths():
    root = Path(__file__).resolve().parents[1]
    source = (root / "examples" / "ide_native_v4.py").read_text(encoding="utf-8")
    for name in (
        "ide_workspace_session", "ide_workspace_preview", "ide_core_persistent",
        "ide_core_read_bridge", "ide_project_runner", "ide_debug_process_client",
        "ide_tooling_navigation", "ide_tooling_diagnostics", "ide_tooling_symbols",
    ):
        assert f"from zunyite_gui.{name} import" in source, name
        assert f"from pynix_gui.{name} import" not in source, name


def test_canonical_imports_work_in_fresh_interpreter_before_legacy_import():
    import subprocess
    import sys

    code = (
        "import zunyite_gui.wrap_engine as canonical_wrap; "
        "import zunyite_gui.text_metrics as canonical_metrics; "
        "from zunyite_gui.ide_project_runner import ProjectRunner; "
        "from zunyite_gui.ide_debug_process_client import DebugProcessClient; "
        "import pynix_gui.wrap_engine as old_wrap; "
        "import pynix_gui.text_metrics as old_metrics; "
        "assert canonical_wrap.GUIWrappedText is old_wrap.GUIWrappedText; "
        "assert canonical_metrics.GUITextMetrics is old_metrics.GUITextMetrics; "
        "assert canonical_wrap.GUIWrappedText.__module__ == 'zunyite_gui.wrap_engine'"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_legacy_workspace_session_uses_canonical_document_and_error_types():
    from pynix_gui.ide_workspace_session import WorkspaceSession, WorkspaceDocument, WorkspaceError
    from zunyite_gui.ide_workspace_session import (
        WorkspaceSession as CanonicalSession,
        WorkspaceDocument as CanonicalDocument,
        WorkspaceError as CanonicalError,
    )

    assert WorkspaceSession is CanonicalSession
    assert WorkspaceDocument is CanonicalDocument
    assert WorkspaceError is CanonicalError
    assert WorkspaceDocument.__module__ == "zunyite_gui.ide_workspace_session"
    assert WorkspaceError.__module__ == "zunyite_gui.ide_workspace_session"


def test_legacy_run_controller_still_exposes_canonical_error_and_subprocess():
    import pynix_gui.ide_project_runner as legacy
    import zunyite_gui.ide_project_runner as canonical

    assert legacy.ProjectRunner is canonical.ProjectRunner
    assert legacy.RunError is canonical.RunError
    assert legacy.RunError.__module__ == "zunyite_gui.ide_project_runner"
    # Older test integrations patch this module-level subprocess reference.
    assert legacy.subprocess is canonical.subprocess


def test_persistent_core_and_snapshot_errors_share_canonical_identity():
    import pynix_gui.ide_core_persistent as old_core
    import zunyite_gui.ide_core_persistent as new_core
    import pynix_gui.ide_core_read_bridge as old_bridge
    import zunyite_gui.ide_core_read_bridge as new_bridge

    assert old_core.PersistentCoreReader is new_core.PersistentCoreReader
    assert old_bridge.CoreSnapshotError is new_bridge.CoreSnapshotError
    assert new_bridge.CoreSnapshotError.__module__ == "zunyite_gui.ide_core_read_bridge"
    assert new_core.PersistentCoreReader.__module__ == "zunyite_gui.ide_core_persistent"
    assert new_core.CoreSnapshotError is new_bridge.CoreSnapshotError


def test_canonical_tooling_modules_keep_legacy_import_identity_and_protocol():
    from zunyite_gui.ide_tooling_diagnostics import Problem, DiagnosticSnapshot, read_diagnostics
    from pynix_gui.ide_tooling_diagnostics import (
        Problem as LegacyProblem, DiagnosticSnapshot as LegacySnapshot,
        read_diagnostics as legacy_diagnostics,
    )
    from zunyite_gui.ide_tooling_navigation import query_navigation
    from pynix_gui.ide_tooling_navigation import query_navigation as legacy_navigation
    from zunyite_gui.ide_tooling_symbols import read_symbols
    from pynix_gui.ide_tooling_symbols import read_symbols as legacy_symbols

    assert Problem is LegacyProblem
    assert DiagnosticSnapshot is LegacySnapshot
    assert read_diagnostics is legacy_diagnostics
    assert query_navigation is legacy_navigation
    assert read_symbols is legacy_symbols
    assert Problem.__module__ == "zunyite_gui.ide_tooling_diagnostics"

    import pynix_gui.ide_tooling_symbols as legacy_module
    import zunyite_gui.ide_tooling_symbols as canonical_module
    assert legacy_module.subprocess is canonical_module.subprocess


def test_debugger_migration_uses_single_module_object_and_patchable_worker():
    import pynix_gui.ide_debug_process_client as old_debug
    import zunyite_gui.ide_debug_process_client as new_debug

    assert old_debug is new_debug
    assert old_debug.DebugProcessClient is new_debug.DebugProcessClient
    assert new_debug.DebugProcessClient.__module__ == "zunyite_gui.ide_debug_process_client"
    assert old_debug.DebugClientError is new_debug.DebugClientError
    assert old_debug._Worker is new_debug._Worker


def test_debugger_legacy_patch_is_visible_to_canonical_launch(tmp_path, monkeypatch):
    import pynix_gui.ide_debug_process_client as legacy
    from zunyite_gui.ide_debug_process_client import DebugProcessClient

    source = tmp_path / "main.uny"
    source.write_text("function main()\n    print(1)\n", encoding="utf-8")
    used = []

    class FakeWorker:
        def __init__(self, python, root):
            used.append(self)
            self.closed = False

        def start(self):
            pass

        def send(self, packet):
            assert packet["command"] == "launch"

        def receive(self):
            return {"protocol": "pynix-debug", "version": 1,
                    "event": "started", "state": "finished", "output": "1"}

        def close(self):
            self.closed = True

    monkeypatch.setattr(legacy, "_Worker", FakeWorker)
    reply = DebugProcessClient(tmp_path, tmp_path / "compiler_python").launch("main.uny")
    assert reply["state"] == "finished"
    assert len(used) == 1 and used[0].closed


def test_debugger_canonical_and_legacy_module_alias_in_both_import_orders():
    import subprocess
    import sys

    for first, second in (
        ("pynix_gui.ide_debug_process_client", "zunyite_gui.ide_debug_process_client"),
        ("zunyite_gui.ide_debug_process_client", "pynix_gui.ide_debug_process_client"),
    ):
        code = (
            "import importlib, sys; "
            f"a=importlib.import_module({first!r}); "
            f"b=importlib.import_module({second!r}); "
            "assert a is b, (a,b); "
            "assert a.DebugProcessClient is b.DebugProcessClient; "
            "assert a._Worker is b._Worker"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, (first, result.stderr)


def test_git_read_only_services_have_single_canonical_types_and_functions():
    from pynix_gui.ide_git_snapshot import GitSnapshot as LegacySnapshot
    from zunyite_gui.ide_git_snapshot import GitSnapshot as CanonicalSnapshot
    from pynix_gui.ide_git_snapshot import read_git_snapshot as old_snapshot
    from zunyite_gui.ide_git_snapshot import read_git_snapshot as new_snapshot
    from pynix_gui.ide_git_log import GitLogError as LegacyLogError
    from zunyite_gui.ide_git_log import GitLogError as CanonicalLogError
    from pynix_gui.ide_git_log import read_git_log as old_log
    from zunyite_gui.ide_git_log import read_git_log as new_log

    assert LegacySnapshot is CanonicalSnapshot
    assert old_snapshot is new_snapshot
    assert LegacyLogError is CanonicalLogError
    assert old_log is new_log
    assert CanonicalSnapshot.__module__ == "zunyite_gui.ide_git_snapshot"
    assert CanonicalLogError.__module__ == "zunyite_gui.ide_git_log"


def test_native_ide_uses_canonical_read_only_git_adapters():
    source = (Path(__file__).resolve().parents[1] / "examples/ide_native_v4.py").read_text(
        encoding="utf-8"
    )
    for name in ("ide_git_snapshot", "ide_git_log"):
        assert f"from zunyite_gui.{name} import" in source
        assert f"from pynix_gui.{name} import" not in source


def test_canonical_file_icon_registry_retains_legacy_type_codes():
    from zunyite_gui.ide_file_icons import ICON_BY_EXTENSION, ICON_TINT, file_icon_type
    from pynix_gui.ide_file_icons import (
        ICON_BY_EXTENSION as old_extensions,
        ICON_TINT as old_tints,
        file_icon_type as old_icon_type,
    )

    assert ICON_BY_EXTENSION is old_extensions
    assert ICON_TINT is old_tints
    assert file_icon_type is old_icon_type
    assert file_icon_type("src/main.uny") == file_icon_type("src/old.pnx")
    assert file_icon_type("src/main.uny") in ICON_TINT


def test_editor_lexer_and_preview_highlighting_share_canonical_exports():
    from zunyite_gui.ide_syntax_highlight import Token, highlight_document
    from pynix_gui.ide_syntax_highlight import (
        Token as LegacyToken, highlight_document as legacy_highlight,
    )
    from zunyite_gui.ide_editor_lexer import EDITOR_LEXER_JS
    from pynix_gui.ide_editor_lexer import EDITOR_LEXER_JS as old_lexer

    assert Token is LegacyToken
    assert highlight_document is legacy_highlight
    assert Token.__module__ == "zunyite_gui.ide_syntax_highlight"
    assert EDITOR_LEXER_JS == old_lexer
    assert "ZUNYITE_KEYWORDS" in EDITOR_LEXER_JS
    assert "PYNIX_KEYWORDS" not in EDITOR_LEXER_JS
    assert "window.pynixHighlightTokens=tokenize;" in EDITOR_LEXER_JS
    preview_source = (
        Path(__file__).resolve().parents[1] / "pynix_gui/ide_workspace_preview.py"
    ).read_text(encoding="utf-8")
    assert "from zunyite_gui.ide_editor_lexer import EDITOR_LEXER_JS" in preview_source
    assert "from zunyite_gui.ide_syntax_highlight import highlight_document" in preview_source
