import numpy as np


class Points:

    def __init__(self, ax, color=None):
        self._ax = ax
        self._fig = self._ax.get_figure()

        self._scatter = None

        self._connections = {}
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

        self.on_button_press = None
        self.on_pick = None

    def _make_scatter(self, x=0, y=0):
        self._scatter = self._ax.scatter([x], [y], picker=True)

    def _on_button_press(self, event):
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata
        if None in (x, y):
            return
        if self._scatter is None:
            self._make_scatter(x=x, y=y)
        else:
            self._persist_dot(x=x, y=y)
        if self.on_button_press is not None:
            self.on_button_press(event)

    def _persist_dot(self, x, y):
        offsets = self._scatter.get_offsets()
        offsets = np.concatenate([offsets, [[x, y]]])
        self._scatter.set_offsets(offsets)

    def _remove_point(self, inds):
        offsets = np.delete(self._scatter.get_offsets(), inds, axis=0)
        self._scatter.set_offsets(offsets)

    def _on_pick(self, event):
        if event.mouseevent.button == 3:
            self._remove_point(event.ind)
        if self.on_pick is not None:
            self.on_pick(event)
