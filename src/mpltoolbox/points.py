import numpy as np


class Points:

    def __init__(self,
                 ax,
                 color=None,
                 on_motion_notify=None,
                 on_button_press=None,
                 on_pick=None):
        self._ax = ax
        self._fig = self._ax.get_figure()

        self._scatter = None

        self._connections = {}
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

        self.on_motion_notify = on_motion_notify
        self.on_button_press = on_button_press
        self.on_pick = on_pick

        self._pick_lock = False
        self._moving_dot_indices = None

    def __del__(self):
        for c in self._connections.values():
            self._fig.canvas.mpl_disconnect(c)
        self._scatter.remove()
        del self._scatter, self._connections
        self._fig.canvas.draw_idle()

    def _make_scatter(self, x=0, y=0):
        self._scatter = self._ax.scatter([x], [y], picker=True)
        self._fig.canvas.draw_idle()

    def _on_button_press(self, event):
        if event.button != 1 or self._pick_lock:
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
        self._fig.canvas.draw_idle()

    def _remove_point(self, inds):
        offsets = np.delete(self._scatter.get_offsets(), inds, axis=0)
        self._scatter.set_offsets(offsets)
        self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        button = event.mouseevent.button
        if button == 1:
            self._pick_lock = True
            self._activate_moving_dot(event)
        if button == 3:
            self._remove_point(event.ind)
        if self.on_pick is not None:
            self.on_pick(event)

    def _activate_moving_dot(self, event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._on_button_release)
        self._moving_dot_indices = event.ind

    def _on_motion_notify(self, event):
        self._move_dot(event)
        if self.on_motion_notify is not None:
            self.on_motion_notify(event)

    def _move_dot(self, event):
        if None in (event.xdata, event.ydata):
            return
        ind = self._moving_dot_indices[0]
        offsets = self._scatter.get_offsets()
        offsets[ind] = [event.xdata, event.ydata]
        self._scatter.set_offsets(offsets)
        self._fig.canvas.draw_idle()

    def _on_button_release(self, event):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        self._pick_lock = False

    def get_point(self, ind):
        return self._scatter.get_offsets()[ind]

    def get_all_points(self):
        return self._scatter.get_offsets()
