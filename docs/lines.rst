Lines
=====

Use the ``Lines`` tool to add lines to a plot:

.. code-block:: python

   import matplotlib.pyplot as plt
   import mpltoolbox as tbx

   fig, ax = plt.subplots()
   ax.set_xlim(0, 100)
   ax.set_ylim(0, 100)

   lines = tbx.Lines(ax=ax, n=2)

.. image:: images/lines01.png
