# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from .utils import make_color
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event


class Lines(Tool):

    def __init__(self, ax: Axes, n: int, color=None, **kwargs):
        super().__init__(ax, **kwargs)
        self._nmax = n
        self.lines = []
        self._pick_lock = False
        self._moving_vertex_index = None
        self._moving_vertex_artist = None
        self._is_points = self._nmax == 1
        self._color = color
        self._line_counter = 0

    def __del__(self):
        super().shutdown(artists=self.lines)

    def _make_new_line(self, x: float, y: float):
        xpos = [x] if self._is_points else [x, x]
        ypos = [y] if self._is_points else [y, y]
        line, = self._ax.plot(xpos,
                              ypos,
                              '-o',
                              color=make_color(color=self._color,
                                               counter=self._line_counter))
        self.lines.append(line)
        self._line_counter += 1

    def _on_motion_notify(self, event: Event):
        self._move_vertex(event=event, ind=-1, line=self.lines[-1])

    def _on_button_press(self, event: Event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        if 'motion_notify_event' not in self._connections:
            self._make_new_line(x=event.xdata, y=event.ydata)
            if self._is_points:
                self._finalize_line(event)
            else:
                self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
                    'motion_notify_event', self._on_motion_notify)
                self._draw()
        else:
            self._persist_dot(event)

    def _persist_dot(self, event: Event):
        if self._get_line_length(-1) == self._nmax:
            self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
            del self._connections['motion_notify_event']
            self._finalize_line(event)
        else:
            new_data = self.lines[-1].get_data()
            self.lines[-1].set_data(
                (np.append(new_data[0],
                           new_data[0][-1]), np.append(new_data[1], new_data[1][-1])))
            self._draw()

    def _finalize_line(self, event):
        self.lines[-1].set_picker(5.0)
        if self.on_create is not None:
            self.on_create(event)
        self._draw()

    def _remove_line(self, line: Artist):
        line.remove()
        self.lines.remove(line)
        self._draw()

    def _on_pick(self, event: Event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        if event.mouseevent.button == 1:
            self._pick_lock = True
            self._grab_vertex(event)
            if self.on_vertex_press is not None:
                self.on_vertex_press(event)
        elif event.mouseevent.button == 2:
            self._remove_line(event.artist)
            if self.on_remove is not None:
                self.on_remove(event)
        elif event.mouseevent.button == 3:
            self._pick_lock = True
            self._grab_line(event)
            if self.on_drag_press is not None:
                self.on_drag_press(event)

    def _grab_vertex(self, event: Event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_vertex_motion)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', partial(self._release_line, kind='vertex'))
        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_artist = event.artist

    def _on_vertex_motion(self, event: Event):
        self._move_vertex(event=event,
                          ind=self._moving_vertex_index,
                          line=self._moving_vertex_artist)
        if self.on_vertex_move is not None:
            self.on_vertex_move(event)

    def _move_vertex(self, event: Event, ind: int, line: Artist):
        if event.inaxes != self._ax:
            return
        new_data = line.get_data()
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        line.set_data(new_data)
        self._draw()

    def _grab_line(self, event: Event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._move_line)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', partial(self._release_line, kind='grab'))
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grab_artist_origin = self._grab_artist.get_data()

    def _move_line(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._grab_artist.set_data(
            (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy))
        self._draw()

    def _release_line(self, event: Event, kind: str):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        del self._connections['motion_notify_event']
        del self._connections['button_release_event']
        self._pick_lock = False
        if (kind == 'vertex') and (self.on_vertex_release is not None):
            self.on_vertex_release(event)
        elif (kind == 'drag') and (self.on_drag_release is not None):
            self.on_drag_release(event)

    def _get_line_length(self, ind: int):
        return len(self.lines[ind].get_xydata())

    def get_line(self, ind: int) -> np.ndarray:
        return self.lines[ind].get_xydata()
