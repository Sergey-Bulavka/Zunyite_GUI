"""Legacy debugger module alias.

The worker factory is a module-level integration hook used by existing
plugins and tests. Both import paths must reference *the same module object*
rather than a star-import shim, so patching _Worker remains effective.
"""
from __future__ import annotations
import sys
from zunyite_gui import ide_debug_process_client as _canonical

sys.modules[__name__] = _canonical
# Preserve `from pynix_gui import ide_debug_process_client` even when the
# legacy package namespace was already imported before this alias.
setattr(sys.modules[__package__], "ide_debug_process_client", _canonical)
