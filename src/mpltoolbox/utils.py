# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)


def make_color(color, counter):
    if color is None:
        return f'C{counter}'
    if callable(color):
        return color()
    if isinstance(color, list):
        return color[counter % len(color)]
    return color
