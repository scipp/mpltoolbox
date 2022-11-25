# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from .event_handler import EventHandler
from .utils import parse_kwargs
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
import uuid
from typing import Tuple


class Line:

    def __init__(self, x: float, y: float, number: int, ax: Axes, n=2, **kwargs):
        self._max_clicks = n
        self._ax = ax
        kwargs = parse_kwargs(kwargs, number)
        if set(['ls', 'linestyle']).isdisjoint(set(kwargs.keys())):
            kwargs['ls'] = 'solid'
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        self._line, = self._ax.plot(x, y, **kwargs)
        self._line.parent = self
        self.id = uuid.uuid1().hex

    def __repr__(self):
        return f'Line: x={self.x}, y={self.y}, color={self.color}'

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self.x)

    @property
    def x(self) -> float:
        return self._line.get_xdata()

    @x.setter
    def x(self, x: float):
        self._line.set_xdata(x)

    @property
    def y(self) -> float:
        return self._line.get_ydata()

    @y.setter
    def y(self, y: float):
        self._line.set_ydata(y)

    @property
    def xy(self) -> float:
        return self._line.get_data()

    @xy.setter
    def xy(self, xy: float):
        self._line.set_data(xy)

    @property
    def color(self) -> str:
        return self._line.get_color()

    @color.setter
    def color(self, c):
        self._line.set_color(c)

    @property
    def markerfacecolor(self) -> str:
        return self._line.get_markerfacecolor()

    @markerfacecolor.setter
    def markerfacecolor(self, color):
        self._line.set_markerfacecolor(color)

    @property
    def markeredgecolor(self) -> str:
        return self._line.get_markeredgecolor()

    @markeredgecolor.setter
    def markerfacecolor(self, color):
        self._line.set_markeredgecolor(color)

    @property
    def mfc(self) -> str:
        return self.markerfacecolor

    @mfc.setter
    def mfc(self, color):
        self.markerfacecolor = color

    @property
    def mec(self) -> str:
        return self.markeredgecolor

    @mec.setter
    def mec(self, color):
        self.markeredgecolor = color

    @property
    def marker(self) -> str:
        return self._line.get_marker()

    @marker.setter
    def marker(self, m):
        self._line.set_marker(m)

    @property
    def linestyle(self) -> str:
        return self._line.get_linestyle()

    @linestyle.setter
    def linestyle(self, style):
        self._line.set_linestyle(style)

    @property
    def ls(self) -> str:
        return self.linestyle

    @ls.setter
    def ls(self, style):
        self.linestyle = style

    @property
    def linewidth(self) -> str:
        return self._line.get_linewidth()

    @linewidth.setter
    def linewidth(self, width):
        self._line.set_linewidth(width)

    @property
    def lw(self) -> str:
        return self.linewidth

    @lw.setter
    def lw(self, width):
        self.linewidth = width

    def remove(self):
        self._line.remove()

    @property
    def artist(self) -> str:
        return self._line

    def set_picker(self, pick):
        self._line.set_picker(pick)

    def is_moveable(self, artist):
        return True

    def is_draggable(self, artist):
        return True

    def is_removable(self, artist):
        return True

    def move_vertex(self, event: Event, ind: int):
        new_data = self.xy
        if ind is None:
            ind = -1
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        self.xy = new_data

    # def move_vertex(self, event: Event, ind: int):
    #     x, y = self._vertices.get_data()
    #     if ind is None:
    #         ind = 2
    #     x[ind] = event.xdata
    #     y[ind] = event.ydata
    #     opp = (ind + 2) % 4
    #     if ind == 0:
    #         width = x[opp] - x[ind]
    #         height = y[opp] - y[ind]
    #     elif ind == 1:
    #         width = x[ind] - x[opp]
    #         height = y[opp] - y[ind]
    #     elif ind == 2:
    #         width = x[ind] - x[opp]
    #         height = y[ind] - y[opp]
    #     elif ind == 3:
    #         width = x[opp] - x[ind]
    #         height = y[ind] - y[opp]
    #     xy = (min(x[ind], x[opp]) if width > 0 else max(x[ind], x[opp]),
    #           min(y[ind], y[opp]) if height > 0 else max(y[ind], y[opp]))
    #     self.update(xy=xy, width=width, height=height)

    def after_persist_vertex(self, event):
        new_data = self.xy
        self.xy = (np.append(new_data[0],
                             new_data[0][-1]), np.append(new_data[1], new_data[1][-1]))
        print(self.xy)
        # self._draw()


Lines = partial(EventHandler, spawner=Line)
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

# class LinesOLD(EventHandler):
#     """
#     Add lines to the supplied axes.

#     Controls:
#       - Left-click to make new lines
#       - Left-click and hold on line vertex to move vertex
#       - Right-click and hold to drag/move the entire line
#       - Middle-click to delete line

#     :param ax: The Matplotlib axes to which the Lines tool will be attached.
#     :param n: The number of vertices for each line. Default is 2.
#     :param autostart: Automatically activate the tool upon creation if `True`.
#     :param on_create: Callback that fires when a line is created.
#     :param on_remove: Callback that fires when a line is removed.
#     :param on_vertex_press: Callback that fires when a vertex is left-clicked.
#     :param on_vertex_move: Callback that fires when a vertex is moved.
#     :param on_vertex_release: Callback that fires when a vertex is released.
#     :param on_drag_press: Callback that fires when a line is right-clicked.
#     :param on_drag_move: Callback that fires when a line is dragged.
#     :param on_drag_release: Callback that fires when a line is released.
#     :param kwargs: Matplotlib line parameters used for customization.
#         Each parameter can be a single item (it will apply to all lines),
#         a list of items (one entry per line), or a callable (which will be
#         called every time a new line is created).
#     """

#     def __init__(self, ax: Axes, n: int = 2, **kwargs):
#         super().__init__(ax, **kwargs)
#         self._spawner = Line
#         self._max_clicks = n

#         # self._maker = Line
#         # self._nmax = n
#         # self.lines = []
#         # self._pick_lock = False
#         # self._moving_vertex_index = None
#         # self._moving_vertex_artist = None

#     def _move_vertex(self, event: Event, ind: int, motif):
#         if event.inaxes != self._ax:
#             return
#         new_data = motif.xy
#         new_data[0][ind] = event.xdata
#         new_data[1][ind] = event.ydata
#         motif.xy = new_data
#         # self._draw()

# class LinesOLD(Tool):
#     """
#     Add lines to the supplied axes.

#     Controls:
#       - Left-click to make new lines
#       - Left-click and hold on line vertex to move vertex
#       - Right-click and hold to drag/move the entire line
#       - Middle-click to delete line

#     :param ax: The Matplotlib axes to which the Lines tool will be attached.
#     :param n: The number of vertices for each line. Default is 2.
#     :param autostart: Automatically activate the tool upon creation if `True`.
#     :param on_create: Callback that fires when a line is created.
#     :param on_remove: Callback that fires when a line is removed.
#     :param on_vertex_press: Callback that fires when a vertex is left-clicked.
#     :param on_vertex_move: Callback that fires when a vertex is moved.
#     :param on_vertex_release: Callback that fires when a vertex is released.
#     :param on_drag_press: Callback that fires when a line is right-clicked.
#     :param on_drag_move: Callback that fires when a line is dragged.
#     :param on_drag_release: Callback that fires when a line is released.
#     :param kwargs: Matplotlib line parameters used for customization.
#         Each parameter can be a single item (it will apply to all lines),
#         a list of items (one entry per line), or a callable (which will be
#         called every time a new line is created).
#     """

#     def __init__(self, ax: Axes, n: int = 2, **kwargs):
#         super().__init__(ax, **kwargs)
#         self._maker = Line
#         self._nmax = n
#         self.lines = []
#         self._pick_lock = False
#         self._moving_vertex_index = None
#         self._moving_vertex_artist = None

#     def __del__(self):
#         super().shutdown(artists=self.lines)

#     def _on_button_press(self, event: Event):
#         if event.button != 1 or self._pick_lock or self._get_active_tool():
#             return
#         if event.inaxes != self._ax:
#             return
#         if 'motion_notify_event' not in self._connections:
#             self._make_new_line(x=event.xdata, y=event.ydata)
#             # self._after_line_creation(event)
#             self._connect({'motion_notify_event': self._on_motion_notify})
#         #     self._draw()
#         # else:
#         self._persist_vertex(event)

#     # def _new_line_pos(self, x: float, y: float) -> Tuple[float]:
#     #     return [x, x], [y, y]

#     def _make_new_line(self, x: float, y: float):
#         # xpos, ypos = self._new_line_pos(x, y)
#         kwargs = self._parse_kwargs()
#         if set(['ls', 'linestyle']).isdisjoint(set(kwargs.keys())):
#             kwargs['ls'] = 'solid'
#         if 'marker' not in kwargs:
#             kwargs['marker'] = 'o'
#         line = self._maker(x, y, ax=self._ax, **kwargs)
#         # line.id = str(uuid.uuid1())
#         self.lines.append(line)
#         self._artist_counter += 1

#     def _on_motion_notify(self, event: Event):
#         self._move_vertex(event=event, ind=-1, artist=self.lines[-1].artist)

#     # def _after_line_creation(self, event: Event):
#     #     self._connect({'motion_notify_event': self._on_motion_notify})
#     #     self._draw()

#     def _duplicate_last_vertex(self):
#         new_data = self.lines[-1].xy
#         self.lines[-1].xy = (np.append(new_data[0], new_data[0][-1]),
#                              np.append(new_data[1], new_data[1][-1]))
#         self._draw()

#     def _persist_vertex(self, event: Event):
#         # if self._get_line_length(-1) == self._nmax:
#         if len(self.lines[-1]) == self._nmax:
#             self._disconnect(['motion_notify_event'])
#             self._finalize_line(event)
#         else:
#             self._duplicate_last_vertex()

#     def _finalize_line(self, event: Event):
#         self.lines[-1].artist.set_picker(5.0)
#         if self.on_create is not None:
#             self.call_on_create({'event': event, 'artist': self.lines[-1]})
#         self._draw()

#     def _remove_line(self, line: Artist):
#         line.parent.remove()
#         self.lines.remove(line.parent)
#         # if draw:
#         self._draw()

#     def _on_pick(self, event: Event):
#         if self._get_active_tool():
#             return
#         if event.mouseevent.inaxes != self._ax:
#             return
#         if event.mouseevent.button == 1:
#             self._pick_lock = True
#             self._grab_vertex(event)
#             if self.on_vertex_press is not None:
#                 self.call_on_vertex_press({
#                     'event': event,
#                     'ind': self._moving_vertex_index,
#                     'artist': self._moving_vertex_artist
#                 })
#         elif event.mouseevent.button == 2:
#             self._remove_line(event.artist)
#             if self.on_remove is not None:
#                 self.call_on_remove({'event': event, 'artist': event.artist})
#         elif event.mouseevent.button == 3:
#             self._pick_lock = True
#             self._grab_line(event)
#             if self.on_drag_press is not None:
#                 self.call_on_drag_press({'event': event, 'artist': self._grab_artist})

#     def _grab_vertex(self, event: Event):
#         self._connect({
#             'motion_notify_event': self._on_vertex_motion,
#             'button_release_event': partial(self._release_line, kind='vertex')
#         })

#         self._moving_vertex_index = event.ind[0]
#         self._moving_vertex_artist = event.artist

#     def _on_vertex_motion(self, event: Event):
#         event_dict = {
#             'event': event,
#             'ind': self._moving_vertex_index,
#             'artist': self._moving_vertex_artist
#         }
#         self._move_vertex(**event_dict)
#         if self.on_vertex_move is not None:
#             self.call_on_vertex_move(event_dict)
#         if self.on_change is not None:
#             self.call_on_change(self._moving_vertex_artist.parent)

#     def _move_vertex(self, event: Event, ind: int, artist: Artist):
#         if event.inaxes != self._ax:
#             return
#         new_data = artist.get_data()
#         new_data[0][ind] = event.xdata
#         new_data[1][ind] = event.ydata
#         artist.parent.xy = new_data
#         self._draw()

#     def _grab_line(self, event: Event):
#         self._connect({
#             'motion_notify_event': self._move_line,
#             'button_release_event': partial(self._release_line, kind='drag')
#         })

#         self._grab_artist = event.artist  #._line # getattr(event.artist, '_line', event.artist)
#         self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
#         self._grab_artist_origin = self._grab_artist.get_data()

#     def _move_line(self, event: Event, draw: bool = True):
#         if event.inaxes != self._ax:
#             return
#         dx = event.xdata - self._grab_mouse_origin[0]
#         dy = event.ydata - self._grab_mouse_origin[1]
#         self._grab_artist.parent.xy = (self._grab_artist_origin[0] + dx,
#                                        self._grab_artist_origin[1] + dy)
#         if draw:
#             self._draw()
#         if self.on_drag_move is not None:
#             self.call_on_drag_move({'event': event, 'artist': self._grab_artist})
#         if self.on_change is not None:
#             self.call_on_change(self._grab_artist.parent)

#     def _release_line(self, event: Event, kind: str):
#         self._disconnect(['motion_notify_event', 'button_release_event'])
#         self._pick_lock = False
#         if (kind == 'vertex') and (self.on_vertex_release is not None):
#             self.call_on_vertex_release({
#                 'event': event,
#                 'ind': self._moving_vertex_index,
#                 'artist': self._moving_vertex_artist
#             })
#         elif (kind == 'drag') and (self.on_drag_release is not None):
#             self.call_on_drag_release({'event': event, 'artist': self._grab_artist})

#     # def _get_line_length(self, ind: int):
#     #     return len(self.lines[ind].get_xydata())
