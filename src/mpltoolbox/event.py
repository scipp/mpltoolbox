from dataclasses import dataclass
from matplotlib.pyplot import Axes


@dataclass
class DummyEvent:
    """
    A dummy event class for simulating clicks on figures.
    """
    button: int
    inaxes: Axes
    xdata: float
    ydata: float
