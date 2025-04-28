# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)
# ruff: noqa: E402, F401, I

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from .ellipses import Ellipses
from .event import DummyEvent
from .hspans import Hspans
from .lines import Lines
from .points import Points
from .polygons import Polygons
from .rectangles import Rectangles
from .tool import Tool
from .vspans import Vspans

__all__ = [
    "DummyEvent",
    "Ellipses",
    "Hspans",
    "Lines",
    "Points",
    "Polygons",
    "Rectangles",
    "Tool",
    "Vspans",
]

del importlib
