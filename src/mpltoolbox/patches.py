# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from abc import abstractmethod


class Patches(Tool):

    def __init__(self, ax, patch, **kwargs):

        super().__init__(ax=ax, **kwargs)

        self._patch = patch
        self.patches = []
        self._drag_patch = False
        self._grab_artist = None
        self._grab_mouse_origin = None
        self._grab_artist_origin = None
        self._pick_lock = False

    def __del__(self):
        super().shutdown(artists=self.patches)

    def _on_button_press(self, event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        self._make_new_patch(x=event.xdata, y=event.ydata)
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._persist_patch)

    def _make_new_patch(self, x, y):
        self.patches.append(
            self._patch((x, y), 0, 0, fc=(0, 0, 0, 0.1), ec=(0, 0, 0, 1), picker=True))
        self._ax.add_patch(self.patches[-1])
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._draw()

    def _on_motion_notify(self, event):
        self._resize_patch(event)

    def _resize_patch(self, event):
        if event.inaxes != self._ax:
            return
        x, y = self.patches[-1].xy
        self.patches[-1].set_width(event.xdata - x)
        self.patches[-1].set_height(event.ydata - y)
        self._draw()

    def _persist_patch(self, event=None):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        del self._connections['motion_notify_event']
        del self._connections['button_release_event']
        if (event is not None) and (self.on_create is not None):
            self.on_create(event)

    def _remove_patch(self, rect):
        rect.remove()
        self.patches.remove(rect)
        self._draw()

    def _on_pick(self, event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        if event.mouseevent.button == 3:
            self._pick_lock = True
            self._grab_patch(event)
            if self.on_drag_press is not None:
                self.on_drag_press(event)
        elif event.mouseevent.button == 2:
            self._remove_patch(event.artist)
            if self.on_remove is not None:
                self.on_remove(event)

    def _grab_patch(self, event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._move_patch)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._release_patch)
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata

    def _move_patch(self, event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._update_artist_position(dx, dy)
        self._draw()
        if self.on_drag_move is not None:
            self.on_drag_move(event)

    @abstractmethod
    def _update_artist_position(self, dx, dy):
        return

    def _release_patch(self, event):
        self._persist_patch()
        self._pick_lock = False
        if self.on_drag_release is not None:
            self.on_drag_release(event)

    def get(self, ind):
        return self.patches[ind]
