import numpy as np
from matplotlib.patches import Rectangle


class Rectangles:

    def __init__(self, ax):
        self._ax = ax
        self._fig = ax.get_figure()

        self.rectangles = []

        self._connections = {}
        # self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
        #     'motion_notify_event', self._on_motion_notify)
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

        self.on_motion_notify = None
        self.on_button_press = None
        self.on_pick = None

        self._active_line_drawing = False

    def _make_new_rectangle(self, x=0, y=0):
        self.rectangles.append(
            Rectangle((x, y), 0, 0, fc=(0, 0, 0, 0.1), ec=(0, 0, 0, 1), picker=True))
        self._ax.add_patch(self.rectangles[-1])
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._fig.canvas.draw_idle()

    def _on_motion_notify(self, event):
        self._resize_rectangle(event)
        if self.on_motion_notify is not None:
            self.on_motion_notify(event)

    def _resize_rectangle(self, event):
        if None in (event.xdata, event.ydata):
            return
        x, y = self.rectangles[-1].xy
        self.rectangles[-1].set_width(event.xdata - x)
        self.rectangles[-1].set_height(event.ydata - y)
        # new_data[0][-1] = event.xdata
        # new_data[1][-1] = event.ydata
        # self.lines[-1].set_data(new_data)
        # self._fig.canvas.draw_idle()

    def _on_button_press(self, event):
        if event.button != 1:
            return
        if None in (event.xdata, event.ydata):
            return
        if 'motion_notify_event' not in self._connections:
            self._make_new_rectangle(x=event.xdata, y=event.ydata)
            self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
                'motion_notify_event', self._on_motion_notify)
        else:
            self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
            del self._connections['motion_notify_event']
            # self._persist_dot(event)
        if self.on_button_press is not None:
            self.on_button_press(event)

    # def _persist_dot(self, event):
    #     if None in (event.xdata, event.ydata):
    #         return
    #     if self._get_line_length(-1) == self._nmax:
    #         self._active_line_drawing = False
    #         self.lines[-1].set_picker(5.0)
    #     else:
    #         new_data = self.lines[-1].get_data()
    #         self.lines[-1].set_data(
    #             (np.append(new_data[0],
    #                        new_data[0][-1]), np.append(new_data[1], new_data[1][-1])))
    #     self._fig.canvas.draw_idle()

    def _remove_rectangle(self, rect):
        # self._ax.lines.remove(line)
        rect.remove()
        self.rectangles.remove(rect)
        # self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        print("picked", event)
        if event.mouseevent.button == 3:
            self._remove_rectangle(event.artist)
        if self.on_pick is not None:
            self.on_pick(event)

    # def _get_line_length(self, ind):
    #     return len(self.lines[ind].get_xydata())

    def get_rectangle(self, ind):
        return self.rectangles[ind]
