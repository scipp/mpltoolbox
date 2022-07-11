# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from .utils import make_color
from abc import abstractmethod
from matplotlib.patches import Patch
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb


class Patches(Tool):

    def __init__(self, ax: Axes, patch: Patch, color=None, alpha=0.05, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._patch = patch
        self.patches = []
        self._drag_patch = False
        self._grab_artist = None
        self._grab_mouse_origin = None
        self._grab_artist_origin = None
        self._pick_lock = False
        self._patch_counter = 0
        self._color = color
        self._alpha = alpha

    def __del__(self):
        super().shutdown(artists=self.patches)

    def _on_button_press(self, event: Event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        self._make_new_patch(x=event.xdata, y=event.ydata)
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._persist_patch)

    def _make_new_patch(self, x: float, y: float):
        ec = make_color(color=self._color, counter=self._patch_counter)
        fc = to_rgb(ec) + (self._alpha, )
        self.patches.append(self._patch((x, y), 0, 0, fc=fc, ec=ec, picker=True))
        self._patch_counter += 1
        self._ax.add_patch(self.patches[-1])
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._draw()

    def _on_motion_notify(self, event: Event):
        self._resize_patch(event)

    def _resize_patch(self, event: Event):
        if event.inaxes != self._ax:
            return
        x, y = self.patches[-1].xy
        self.patches[-1].set_width(event.xdata - x)
        self.patches[-1].set_height(event.ydata - y)
        self._draw()

    def _persist_patch(self, event: Event = None):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        del self._connections['motion_notify_event']
        del self._connections['button_release_event']
        if (event is not None) and (self.on_create is not None):
            self.on_create(event)

    def _remove_patch(self, rect: Artist):
        rect.remove()
        self.patches.remove(rect)
        self._draw()

    def _on_pick(self, event: Event):
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

    def _grab_patch(self, event: Event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._move_patch)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._release_patch)
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata

    def _move_patch(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._update_artist_position(dx, dy)
        self._draw()
        if self.on_drag_move is not None:
            self.on_drag_move(event)

    @abstractmethod
    def _update_artist_position(self, dx: float, dy: float):
        return

    def _release_patch(self, event: Event):
        self._persist_patch()
        self._pick_lock = False
        if self.on_drag_release is not None:
            self.on_drag_release(event)

    def get(self, ind: int) -> Patch:
        return self.patches[ind]
