*********************************************
Mpltoolbox - Interactive tools for Matplotlib
*********************************************

Mpltoolbox aims to provide some basic tools
(that other libraries such as
`bokeh <http://docs.bokeh.org/en/latest/>`_ or
`plotly <https://plotly.com/python/>`_ support)
for drawing points, lines, rectangles, polygons on Matplotlib figures.

There are many interactive examples in the Matplotlib
`documentation pages <https://matplotlib.org/stable/gallery/index.html#event-handling>`_,
but the code snippets are often long and potentially not straightforward to maintain.

With ``mpltoolbox``, activating these tools should (hopefully) just be a on-liner.

Installation
============

You can install from ``pip`` using

.. code-block:: sh

   pip install mpltoolbox

or from ``conda`` with

.. code-block:: sh

   conda install -c conda-forge mpltoolbox

Example
=======

.. code-block:: python

   import matplotlib.pyplot as plt
   import mpltoolbox as tbx
   %matplotlib widget

   fig, axes = plt.subplots(2, 2, figsize=(12, 8))
   for ax in axes.flat:
       ax.set_xlim(0, 100)
       ax.set_ylim(0, 100)

   points = tbx.Points(ax=axes[0, 0])
   lines = tbx.Lines(ax=axes[1, 1])
   rects = tbx.Rectangles(ax=axes[0, 1])
   ells = tbx.Ellipses(ax=axes[1, 0])

|points| |rectangles|
|ellipses| |lines|

.. |points| image:: _images/points_4_0.png
   :width: 49%

.. |rectangles| image:: _images/rectangles_4_0.png
   :width: 49%

.. |ellipses| image:: _images/ellipses_4_0.png
   :width: 49%

.. |lines| image:: _images/lines_4_0.png
   :width: 49%

.. toctree::
   :maxdepth: 2
   :hidden:

   points

.. toctree::
   :maxdepth: 2
   :hidden:

   lines

.. toctree::
   :maxdepth: 2
   :hidden:

   rectangles

.. toctree::
   :maxdepth: 2
   :hidden:

   ellipses

.. toctree::
   :maxdepth: 2
   :hidden:

   polygons

.. toctree::
   :maxdepth: 2
   :hidden:

   spans

.. toctree::
   :maxdepth: 2
   :hidden:

   callbacks

.. toctree::
   :maxdepth: 2
   :hidden:

   programmatic-control

.. toctree::
   :maxdepth: 2
   :hidden:

   api

.. toctree::
   :hidden:

   Release notes <https://github.com/scipp/mpltoolbox/releases>
