[![PyPI version](https://badge.fury.io/py/mpltoolbox.svg)](https://pypi.org/project/mpltoolbox)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/mpltoolbox/badges/version.svg)](https://anaconda.org/conda-forge/mpltoolbox)
[![Documentation Status](https://readthedocs.org/projects/mpltoolbox/badge/?version=latest)](https://mpltoolbox.readthedocs.io/en/latest/?badge=latest)
[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)

# mpltoolbox

Mpltoolbox aims to provide some basic tools (that other libraries such as bokeh or plotly support) for drawing points, lines, rectangles, polygons on Matplotlib figures.

There are many interactive examples in the Matplotlib documentation pages,
but the code snippets are often long and potentially not straightforward to maintain.

With `mpltoolbox`, activating these tools should (hopefully) just be a one-liner.

## Documentation

The documentation for `mpltoolbox` can be found at https://mpltoolbox.readthedocs.io.

## Installation

```sh
pip install mpltoolbox
```

## Examples

```Py
import matplotlib.pyplot as plt
import mpltoolbox as tbx
%matplotlib widget
```

### Points

```Py
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

points = tbx.Points(ax=ax)
```

![points](https://mpltoolbox.readthedocs.io/en/latest/_images/points_4_0.png)


### Lines

```Py
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

lines = tbx.Lines(ax=ax, n=2)
```

![lines](https://mpltoolbox.readthedocs.io/en/latest/_images/lines_4_0.png)

### Rectangles

```Py
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

rectangles = tbx.Rectangles(ax=ax)
```

![rects](https://mpltoolbox.readthedocs.io/en/latest/_images/rectangles_4_0.png)

### Ellipses

```Py
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

ellipses = tbx.Ellipses(ax=ax)
```

![ellipses](https://mpltoolbox.readthedocs.io/en/latest/_images/ellipses_4_0.png)
