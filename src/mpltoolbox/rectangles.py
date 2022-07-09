# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from matplotlib.patches import Rectangle


class Rectangles(Tool):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.rectangles = []
        self._drag_rectangle = False
        self._grab_artist = None
        self._grab_mouse_origin = None
        self._grab_artist_origin = None
        self._pick_lock = False

    def __del__(self):
        super().shutdown(artists=self.rectangles)

    def _on_button_press(self, event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        self._make_new_rectangle(x=event.xdata, y=event.ydata)
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._persist_rectangle)

    def _make_new_rectangle(self, x=0, y=0):
        self.rectangles.append(
            Rectangle((x, y), 0, 0, fc=(0, 0, 0, 0.1), ec=(0, 0, 0, 1), picker=True))
        self._ax.add_patch(self.rectangles[-1])
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._fig.canvas.draw_idle()

    def _on_motion_notify(self, event):
        self._resize_rectangle(event)

    def _resize_rectangle(self, event):
        if event.inaxes != self._ax:
            return
        x, y = self.rectangles[-1].xy
        self.rectangles[-1].set_width(event.xdata - x)
        self.rectangles[-1].set_height(event.ydata - y)
        self._fig.canvas.draw_idle()

    def _persist_rectangle(self, event=None):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        del self._connections['motion_notify_event']
        del self._connections['button_release_event']
        if (event is not None) and (self.on_create is not None):
            self.on_create(event)

    def _remove_rectangle(self, rect):
        rect.remove()
        self.rectangles.remove(rect)
        self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        if event.mouseevent.button == 3:
            self._pick_lock = True
            self._grab_rectangle(event)
            if self.on_drag_press is not None:
                self.on_drag_press(event)
        elif event.mouseevent.button == 2:
            self._remove_rectangle(event.artist)
            if self.on_remove is not None:
                self.on_remove(event)

    def _grab_rectangle(self, event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._move_rectangle)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._release_rectangle)
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grab_artist_origin = self._grab_artist.xy

    def _move_rectangle(self, event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._grab_artist.xy = (self._grab_artist_origin[0] + dx,
                                self._grab_artist_origin[1] + dy)
        self._fig.canvas.draw_idle()
        if self.on_drag_move is not None:
            self.on_drag_move(event)

    def _release_rectangle(self, event):
        self._persist_rectangle()
        self._pick_lock = False
        if self.on_drag_release is not None:
            self.on_drag_release(event)

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
