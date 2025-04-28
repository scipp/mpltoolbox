# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)
# ruff: noqa: E402, F401, I

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from .event import DummyEvent
from .tool import Tool
from .lines import Lines
from .rectangles import Rectangles
from .ellipses import Ellipses
from .points import Points
from .polygons import Polygons
from .hspans import Hspans
from .vspans import Vspans

__all__ = [
    "DummyEvent",
    "Tool",
    "Lines",
    "Rectangles",
    "Ellipses",
    "Points",
    "Polygons",
    "Hspans",
    "Vspans",
]

del importlib
