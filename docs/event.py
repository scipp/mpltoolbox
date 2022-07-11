from dataclasses import dataclass
from matplotlib.pyplot import Axes


@dataclass
class Event:
    inaxes: Axes
    xdata: float
    ydata: float
