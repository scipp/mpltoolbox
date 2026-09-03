# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)

from functools import partial

import matplotlib.pyplot as plt
import pytest
from matplotlib.backend_bases import MouseButton

import mpltoolbox as tbx


@pytest.mark.parametrize(
    ("make_tool", "vertices", "target"),
    [
        pytest.param(tbx.Points, [(20, 20)], (20, 20), id="points"),
        pytest.param(
            partial(tbx.Lines, n=2),
            [(10, 10), (30, 30)],
            (20, 20),
            id="lines",
        ),
        pytest.param(
            tbx.Rectangles,
            [(10, 10), (30, 30)],
            (20, 20),
            id="rectangles",
        ),
        pytest.param(
            tbx.Ellipses,
            [(10, 10), (30, 30)],
            (20, 20),
            id="ellipses",
        ),
        pytest.param(
            tbx.Hspans,
            [(20, 10), (20, 30)],
            (20, 20),
            id="hspans",
        ),
        pytest.param(
            tbx.Vspans,
            [(10, 20), (30, 20)],
            (20, 20),
            id="vspans",
        ),
        pytest.param(
            tbx.Polygons,
            [(10, 10), (30, 10), (20, 30), (10, 10)],
            (20, 15),
            id="polygons",
        ),
    ],
)
def test_middle_click_removes_owner_and_calls_callback(make_tool, vertices, target):
    _, ax = plt.subplots()
    ax.set(xlim=(-100, 200), ylim=(-100, 200))
    removed = []
    tool = make_tool(ax=ax, on_remove=removed.append)
    for vertex in vertices:
        tool.click(vertex)
    owner = tool.children[0]

    tool.click(target, button=MouseButton.MIDDLE)

    assert tool.children == []
    assert removed == [owner]
