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


def parse_kwargs(kwargs, counter):
    # if color is None:
    #     return f'C{counter}'
    parsed = {}
    for key, value in kwargs.items():
        if callable(value):
            parsed[key] = value()
        elif isinstance(value, list):
            parsed[key] = value[counter % len(value)]
        else:
            parsed[key] = value
    return parsed
