# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Scipp contributors (https://github.com/scipp)


def parse_kwargs(kwargs: dict, number: int) -> dict:
    parsed = {}
    for key, value in kwargs.items():
        if callable(value):
            parsed[key] = value()
        elif isinstance(value, list):
            parsed[key] = value[number % len(value)]
        else:
            parsed[key] = value
    return parsed
