from dataclasses import dataclass
from matplotlib.pyplot import Axes


@dataclass
class Event:
    button: int
    inaxes: Axes
    xdata: float
    ydata: float
