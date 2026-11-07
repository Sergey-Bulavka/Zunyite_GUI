"""Legacy semantic-rename module alias.

Both import paths share one module object to preserve query_navigation patch
hooks and the RenamePlanError exception identity.
"""
from __future__ import annotations
import sys
from zunyite_gui import ide_semantic_rename as _canonical

sys.modules[__name__] = _canonical
setattr(sys.modules[__package__], "ide_semantic_rename", _canonical)
