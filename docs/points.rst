Points
======

Use the ``Points`` tool to add markers to a plot:

.. code-block:: python

   import matplotlib.pyplot as plt
   import mpltoolbox as tbx
   %matplotlib widget

   fig, ax = plt.subplots()
   ax.set_xlim(0, 100)
   ax.set_ylim(0, 100)

   points = tbx.Points(ax=ax)

.. image:: images/points.png
