import numpy as np


class Lines:

    def __init__(self,
                 ax,
                 n,
                 on_motion_notify=None,
                 on_button_press=None,
                 on_pick=None):
        self._ax = ax
        self._fig = ax.get_figure()
        self._nmax = n

        self.lines = []

        self._connections = {}
        # self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
        #     'motion_notify_event', self._on_motion_notify)
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

        self.on_motion_notify = on_motion_notify
        self.on_button_press = on_button_press
        self.on_pick = on_pick

        # self._active_line_drawing = False

    def __del__(self):
        for c in self._connections.values():
            self._fig.canvas.mpl_disconnect(c)
        for line in self.lines:
            line.remove()
        del self.lines, self._connections

    def _make_new_line(self, x=0, y=0):
        line = self._ax.plot([x, x], [y, y], 'o', ls='solid')[0]
        self.lines.append(line)

    def _on_motion_notify(self, event):
        self._move_dot(event)
        if self.on_motion_notify is not None:
            self.on_motion_notify(event)

    def _move_dot(self, event):
        if None in (event.xdata, event.ydata):  # or (not self._active_line_drawing):
            return
        new_data = self.lines[-1].get_data()
        new_data[0][-1] = event.xdata
        new_data[1][-1] = event.ydata
        self.lines[-1].set_data(new_data)
        self._fig.canvas.draw_idle()

    def _on_button_press(self, event):
        if event.button != 1:
            return
        if None in (event.xdata, event.ydata):
            return
        # if not self._active_line_drawing:
        if 'motion_notify_event' not in self._connections:
            self._make_new_line(x=event.xdata, y=event.ydata)
            # self._active_line_drawing = True
            self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
                'motion_notify_event', self._on_motion_notify)
            self._fig.canvas.draw_idle()
        else:
            self._persist_dot(event)
        if self.on_button_press is not None:
            self.on_button_press(event)

    def _persist_dot(self, event):
        if None in (event.xdata, event.ydata):
            return
        if self._get_line_length(-1) == self._nmax:
            # self._active_line_drawing = False
            self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
            del self._connections['motion_notify_event']
            self.lines[-1].set_picker(5.0)
        else:
            new_data = self.lines[-1].get_data()
            self.lines[-1].set_data(
                (np.append(new_data[0],
                           new_data[0][-1]), np.append(new_data[1], new_data[1][-1])))
        self._fig.canvas.draw_idle()

    def _remove_line(self, line):
        # self._ax.lines.remove(line)
        line.remove()
        self.lines.remove(line)
        self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        if event.mouseevent.button == 3:
            self._remove_line(event.artist)
        if self.on_pick is not None:
            self.on_pick(event)

    def _get_line_length(self, ind):
        return len(self.lines[ind].get_xydata())

    def get_line(self, ind):
        return self.lines[ind].get_xydata()
