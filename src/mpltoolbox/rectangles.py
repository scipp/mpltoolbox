import numpy as np
from matplotlib.patches import Rectangle


class Rectangles:

    def __init__(self,
                 ax,
                 on_vertex_press=None,
                 on_vertex_move=None,
                 on_vertex_release=None,
                 on_drag_press=None,
                 on_drag_move=None,
                 on_drag_release=None):

        self._ax = ax
        self._fig = ax.get_figure()

        self.rectangles = []

        self._connections = {}
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

        self.on_vertex_press = on_vertex_press
        self.on_vertex_move = on_vertex_move
        self.on_vertex_release = on_vertex_release
        self.on_drag_press = on_drag_press
        self.on_drag_move = on_drag_move
        self.on_drag_release = on_drag_release

    def __del__(self):
        for c in self._connections.values():
            self._fig.canvas.mpl_disconnect(c)
        for rect in self.rectangles:
            rect.remove()
        del self.rectangles, self._connections
        self._fig.canvas.draw_idle()

    def _make_new_rectangle(self, x=0, y=0):
        self.rectangles.append(
            Rectangle((x, y), 0, 0, fc=(0, 0, 0, 0.1), ec=(0, 0, 0, 1), picker=True))
        self._ax.add_patch(self.rectangles[-1])
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._fig.canvas.draw_idle()

    def _on_motion_notify(self, event):
        self._resize_rectangle(event)
        # if self.on_motion_notify is not None:
        #     self.on_motion_notify(event)

    def _resize_rectangle(self, event):
        if None in (event.xdata, event.ydata):
            return
        x, y = self.rectangles[-1].xy
        self.rectangles[-1].set_width(event.xdata - x)
        self.rectangles[-1].set_height(event.ydata - y)
        self._fig.canvas.draw_idle()

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
        # if self.on_button_press is not None:
        #     self.on_button_press(event)

    def _remove_rectangle(self, rect):
        rect.remove()
        self.rectangles.remove(rect)
        self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        if event.mouseevent.button == 3:
            self._remove_rectangle(event.artist)
        # if self.on_pick is not None:
        #     self.on_pick(event)

    def get_rectangle(self, ind):
        rect = self.rectangles[ind]
        box = rect.get_bbox()
        return {
            "xmin": box.xmin,
            "xmax": box.xmax,
            "ymin": box.ymin,
            "ymax": box.ymax,
            "width": abs(rect.get_width()),
            "height": abs(rect.get_height())
        }
