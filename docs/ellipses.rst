Ellipses
========

Use the ``Ellipses`` tool to add ellipses to a plot:

.. code-block:: python

   import matplotlib.pyplot as plt
   import mpltoolbox as tbx
   %matplotlib widget

   fig, ax = plt.subplots()
   ax.set_xlim(0, 100)
   ax.set_ylim(0, 100)

   ellipses = tbx.Ellipses(ax=ax)

.. image:: images/ellipses.png
