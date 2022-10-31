# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
import uuid
from typing import Tuple


class Lines(Tool):
    """
    Add lines to the supplied axes.

    Controls:
      - Left-click to make new lines
      - Left-click and hold on line vertex to move vertex
      - Right-click and hold to drag/move the entire line
      - Middle-click to delete line

    :param ax: The Matplotlib axes to which the Lines tool will be attached.
    :param n: The number of vertices for each line. Default is 2.
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a line is created.
    :param on_remove: Callback that fires when a line is removed.
    :param on_vertex_press: Callback that fires when a vertex is left-clicked.
    :param on_vertex_move: Callback that fires when a vertex is moved.
    :param on_vertex_release: Callback that fires when a vertex is released.
    :param on_drag_press: Callback that fires when a line is right-clicked.
    :param on_drag_move: Callback that fires when a line is dragged.
    :param on_drag_release: Callback that fires when a line is released.
    :param kwargs: Matplotlib line parameters used for customization.
        Each parameter can be a single item (it will apply to all lines),
        a list of items (one entry per line), or a callable (which will be
        called every time a new line is created).
    """

    def __init__(self, ax: Axes, n: int = 2, **kwargs):
        super().__init__(ax, **kwargs)
        self._nmax = n
        self.lines = []
        self._pick_lock = False
        self._moving_vertex_index = None
        self._moving_vertex_artist = None

    def __del__(self):
        super().shutdown(artists=self.lines)

    def _new_line_pos(self, x: float, y: float) -> Tuple[float]:
        return [x, x], [y, y]

    def _make_new_line(self, x: float, y: float):
        xpos, ypos = self._new_line_pos(x, y)
        kwargs = self._parse_kwargs()
        if set(['ls', 'linestyle']).isdisjoint(set(kwargs.keys())):
            kwargs['ls'] = 'solid'
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        line, = self._ax.plot(xpos, ypos, **kwargs)
        line.id = str(uuid.uuid1())
        self.lines.append(line)
        self._artist_counter += 1

    def _on_motion_notify(self, event: Event):
        self._move_vertex(event=event, ind=-1, artist=self.lines[-1])

    def _after_line_creation(self, event: Event):
        self._connect({'motion_notify_event': self._on_motion_notify})
        self._draw()

    def _on_button_press(self, event: Event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        if 'motion_notify_event' not in self._connections:
            self._make_new_line(x=event.xdata, y=event.ydata)
            self._after_line_creation(event)
        else:
            self._persist_dot(event)

    def _duplicate_last_vertex(self):
        new_data = self.lines[-1].get_data()
        self.lines[-1].set_data(
            (np.append(new_data[0],
                       new_data[0][-1]), np.append(new_data[1], new_data[1][-1])))
        self._draw()

    def _persist_dot(self, event: Event):
        if self._get_line_length(-1) == self._nmax:
            self._disconnect(['motion_notify_event'])
            self._finalize_line(event)
        else:
            self._duplicate_last_vertex()

    def _finalize_line(self, event: Event):
        self.lines[-1].set_picker(5.0)
        if self.on_create is not None:
            self.on_create({'event': event, 'artist': self.lines[-1]})
        self._draw()

    def _remove_line(self, line: Artist, draw: bool = True):
        line.remove()
        self.lines.remove(line)
        if draw:
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
                self.on_vertex_press({
                    'event': event,
                    'ind': self._moving_vertex_index,
                    'artist': self._moving_vertex_artist
                })
        elif event.mouseevent.button == 2:
            self._remove_line(event.artist)
            if self.on_remove is not None:
                self.on_remove({'event': event, 'artist': event.artist})
        elif event.mouseevent.button == 3:
            self._pick_lock = True
            self._grab_line(event)
            if self.on_drag_press is not None:
                self.on_drag_press({'event': event, 'artist': self._grab_artist})

    def _grab_vertex(self, event: Event):
        self._connect({
            'motion_notify_event': self._on_vertex_motion,
            'button_release_event': partial(self._release_line, kind='vertex')
        })

        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_artist = event.artist

    def _on_vertex_motion(self, event: Event):
        event_dict = {
            'event': event,
            'ind': self._moving_vertex_index,
            'artist': self._moving_vertex_artist
        }
        self._move_vertex(**event_dict)
        if self.on_vertex_move is not None:
            self.on_vertex_move(event_dict)

    def _move_vertex(self, event: Event, ind: int, artist: Artist):
        if event.inaxes != self._ax:
            return
        new_data = artist.get_data()
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        artist.set_data(new_data)
        self._draw()

    def _grab_line(self, event: Event):
        self._connect({
            'motion_notify_event': self._move_line,
            'button_release_event': partial(self._release_line, kind='drag')
        })

        self._grab_artist = getattr(event.artist, '_line', event.artist)
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grab_artist_origin = self._grab_artist.get_data()

    def _move_line(self, event: Event, draw: bool = True):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._grab_artist.set_data(
            (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy))
        if draw:
            self._draw()

    def _release_line(self, event: Event, kind: str):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        self._pick_lock = False
        if (kind == 'vertex') and (self.on_vertex_release is not None):
            self.on_vertex_release({
                'event': event,
                'ind': self._moving_vertex_index,
                'artist': self._moving_vertex_artist
            })
        elif (kind == 'drag') and (self.on_drag_release is not None):
            self.on_drag_release({'event': event, 'artist': self._grab_artist})

    def _get_line_length(self, ind: int):
        return len(self.lines[ind].get_xydata())
