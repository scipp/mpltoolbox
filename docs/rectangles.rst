Rectangles
==========

Use the ``Rectangles`` tool to add rectangles to a plot:

.. code-block:: python

   import matplotlib.pyplot as plt
   import mpltoolbox as tbx

   fig, ax = plt.subplots()
   ax.set_xlim(0, 100)
   ax.set_ylim(0, 100)

   rectangles = tbx.Rectangles(ax=ax)

.. image:: images/rectangles.png
