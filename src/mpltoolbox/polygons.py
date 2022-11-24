# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from matplotlib import patches as mp
import uuid


class Polygon:

    def __init__(self, x: float, y: float, ax: Axes, line_kwargs, fill_kwargs):
        self._ax = ax
        self._vertices, = self._ax.plot(x, y, **line_kwargs)
        if fill_kwargs['fc'] is None:
            fill_kwargs['fc'] = self._vertices.get_color()
        self._fill, = self._ax.fill(x, y, **fill_kwargs)
        self._fill.parent = self
        self._vertices.parent = self
        self.id = uuid.uuid1().hex

    def __repr__(self):
        return (f'Polygon: x={self.x}, y={self.y}, '
                f'edgecolor={self.edgecolor}, facecolor={self.facecolor}')

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self.x)

    def _update_fill(self):
        # print(self._vertices.get_data())
        self._fill.set_xy(np.array(self._vertices.get_data()).T)

    @property
    def x(self) -> float:
        return self._vertices.get_xdata()

    @x.setter
    def x(self, x: float):
        self._vertices.set_xdata(x)
        self._update_fill()

    @property
    def y(self) -> float:
        return self._vertices.get_ydata()

    @y.setter
    def y(self, y: float):
        self._vertices.set_ydata(y)
        self._update_fill()

    @property
    def xy(self) -> float:
        return self._vertices.get_data()

    @xy.setter
    def xy(self, xy: float):
        self._vertices.set_data(xy)
        self._update_fill()

    @property
    def edgecolor(self) -> str:
        return self._vertices.get_color()

    @edgecolor.setter
    def edgecolor(self, c):
        self._vertices.set_color(c)

    @property
    def facecolor(self) -> str:
        return self._fill.get_facecolor()

    @facecolor.setter
    def facecolor(self, c):
        self._fill.set_facecolor(c)

    @property
    def markerfacecolor(self) -> str:
        return self._vertices.get_markerfacecolor()

    @markerfacecolor.setter
    def markerfacecolor(self, color):
        self._vertices.set_markerfacecolor(color)

    @property
    def markeredgecolor(self) -> str:
        return self._vertices.get_markeredgecolor()

    @markeredgecolor.setter
    def markerfacecolor(self, color):
        self._vertices.set_markeredgecolor(color)

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
        return self._vertices.get_marker()

    @marker.setter
    def marker(self, m):
        self._vertices.set_marker(m)

    @property
    def linestyle(self) -> str:
        return self._vertices.get_linestyle()

    @linestyle.setter
    def linestyle(self, style):
        self._vertices.set_linestyle(style)

    @property
    def ls(self) -> str:
        return self.linestyle

    @ls.setter
    def ls(self, style):
        self.linestyle = style

    @property
    def linewidth(self) -> str:
        return self._vertices.get_linewidth()

    @linewidth.setter
    def linewidth(self, width):
        self._vertices.set_linewidth(width)

    @property
    def lw(self) -> str:
        return self.linewidth

    @lw.setter
    def lw(self, width):
        self.linewidth = width

    def remove(self):
        self._fill.remove()
        self._vertices.remove()

    # @property
    # def artist(self) -> str:
    #     return self._vertices


class Polygons(Tool):
    """
    Add closed polygons to the supplied axes.

    Controls:
      - Left-click to make new polygons
      - Left-click and hold on polygon vertex to move vertex
      - Right-click and hold to drag/move the entire polygon
      - Middle-click to delete polygon

    :param ax: The Matplotlib axes to which the Polygons tool will be attached.
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a polygon is created.
    :param on_remove: Callback that fires when a polygon is removed.
    :param on_vertex_press: Callback that fires when a vertex is left-clicked.
    :param on_vertex_move: Callback that fires when a vertex is moved.
    :param on_vertex_release: Callback that fires when a vertex is released.
    :param on_drag_press: Callback that fires when a polygon is right-clicked.
    :param on_drag_move: Callback that fires when a polygon is dragged.
    :param on_drag_release: Callback that fires when a polygon is released.
    :param kwargs: Matplotlib parameters used for customization.
        Each parameter can be a single item (it will apply to all polygons),
        a list of items (one entry per polygon), or a callable (which will be
        called every time a new polygon is created).
    """

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax, **kwargs)
        self._maker = Polygon
        self.polygons = []
        self._pick_lock = False
        self._moving_vertex_index = None
        self._moving_vertex_artist = None
        self._distance_from_first_point = 0.05
        self._first_point_position = None
        self._persist_polygon = False

    def __del__(self):
        # super().shutdown(artists=self.polygons + [line._fill for line in self.polygons])
        super().shutdown(artists=self.polygons)

    def _on_button_press(self, event: Event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        if 'motion_notify_event' not in self._connections:
            self._make_new_polygon(x=event.xdata, y=event.ydata)
            # self._after_line_creation(event)
            self._connect({'motion_notify_event': self._on_motion_notify})
            self._draw()
        else:
            self._persist_vertex(event)

    def _make_new_polygon(self, x: float, y: float):
        line_kwargs = self._parse_kwargs()
        fill_kwargs = {}
        for arg in ('ec', 'edgecolor', 'fc', 'facecolor', 'alpha'):
            if arg in line_kwargs:
                fill_kwargs[arg] = line_kwargs.pop(arg)
        if set(['mfc', 'markerfacecolor']).isdisjoint(set(line_kwargs.keys())):
            line_kwargs['mfc'] = 'None'
        if set(['ls', 'linestyle']).isdisjoint(set(line_kwargs.keys())):
            line_kwargs['ls'] = 'solid'
        if 'marker' not in line_kwargs:
            line_kwargs['marker'] = 'o'
        if 'alpha' not in fill_kwargs:
            fill_kwargs['alpha'] = 0.05
        if set(['fc', 'facecolor']).isdisjoint(set(fill_kwargs.keys())):
            fill_kwargs['fc'] = None
        # line, = self._ax.plot([x, x], [y, y], **line_kwargs)
        poly = self._maker(x=[x, x],
                           y=[y, y],
                           ax=self._ax,
                           line_kwargs=line_kwargs,
                           fill_kwargs=fill_kwargs)
        self.polygons.append(poly)
        self._artist_counter += 1
        self._first_point_position_data = (x, y)
        self._first_point_position_axes = self._data_to_axes_transform(x, y)
        # fill, = self._ax.fill(line.get_xdata(), line.get_ydata(), **fill_kwargs)
        # line._fill = fill
        # fill._line = line

    def _data_to_axes_transform(self, x, y):
        trans = self._ax.transData.transform((x, y))
        return self._ax.transAxes.inverted().transform(trans)

    def _compute_distance_from_first_point(self, event):
        if event.inaxes != self._ax:
            return np.Inf
        xdisplay, ydisplay = self._data_to_axes_transform(event.xdata, event.ydata)
        dist = np.sqrt((xdisplay - self._first_point_position_axes[0])**2 +
                       (ydisplay - self._first_point_position_axes[1])**2)
        return dist

    def _on_motion_notify(self, event: Event):
        if self._compute_distance_from_first_point(
                event) < self._distance_from_first_point:
            event.xdata = self._first_point_position_data[0]
            event.ydata = self._first_point_position_data[1]
            self._persist_polygon = True
        else:
            self._persist_polygon = False
        self._move_vertex(event=event, ind=-1, artist=self.polygons[-1]._vertices)

    def _duplicate_last_vertex(self):
        new_data = self.polygons[-1].xy
        self.polygons[-1].xy = (np.append(new_data[0], new_data[0][-1]),
                                np.append(new_data[1], new_data[1][-1]))
        self._draw()

    def _persist_vertex(self, event: Event):
        if self._persist_polygon:
            self._disconnect(['motion_notify_event'])
            self._finalize_polygon(event)
            self._persist_polygon = False
        else:
            self._duplicate_last_vertex()

    def _finalize_polygon(self, event: Event):
        self.polygons[-1]._fill.set_picker(5.0)
        self.polygons[-1]._vertices.set_picker(5.0)
        # self.lines[-1].artist.set_picker(5.0)
        if self.on_create is not None:
            self.call_on_create({'event': event, 'artist': self.polygons[-1]})
        self._draw()

    def _remove_polygon(self, artist: Artist):
        artist.parent.remove()
        self.polygons.remove(artist.parent)
        # self._remove_line(line=artist._line, draw=False)
        # artist.remove()
        self._draw()

    def _on_pick(self, event: Event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        is_polygon = isinstance(event.artist, mp.Polygon)
        if event.mouseevent.button == 1:
            if is_polygon:
                return
            self._pick_lock = True
            self._grab_vertex(event)
            if self.on_vertex_press is not None:
                self.call_on_vertex_press({
                    'event': event,
                    'ind': self._moving_vertex_index,
                    'artist': self._moving_vertex_artist
                })
        elif event.mouseevent.button == 2:
            if not is_polygon:
                return
            self._remove_polygon(event.artist)
            if self.on_remove is not None:
                self.call_on_remove({'event': event, 'artist': event.artist})
        elif event.mouseevent.button == 3:
            if not is_polygon:
                return
            self._pick_lock = True
            self._grab_polygon(event)
            if self.on_drag_press is not None:
                self.call_on_drag_press({'event': event, 'artist': self._grab_artist})

    def _grab_vertex(self, event: Event):
        self._connect({
            'motion_notify_event':
            self._on_vertex_motion,
            'button_release_event':
            partial(self._release_polygon, kind='vertex')
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
            self.call_on_vertex_move(event_dict)
        if self.on_change is not None:
            self.call_on_change(self._moving_vertex_artist.parent)

    def _move_vertex(self, event: Event, ind: int, artist: Artist):
        if event.inaxes != self._ax:
            return
        new_data = artist.get_data()
        if ind in (0, len(new_data[0])):
            ind = [0, -1]
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        artist.parent.xy = new_data
        # artist.set_data(new_data)
        # artist._fill.set_xy(np.array(new_data).T)
        self._draw()

    def _grab_polygon(self, event: Event):
        self._connect({
            'motion_notify_event':
            self._move_polygon,
            'button_release_event':
            partial(self._release_polygon, kind='drag')
        })

        # self._grab_artist = getattr(event.artist, '_line', event.artist)
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grab_artist_origin = self._grab_artist.parent.xy
        # print(self._grab_artist_origin)
        # assert False

    def _move_polygon(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._grab_artist.parent.xy = (self._grab_artist_origin[0] + dx,
                                       self._grab_artist_origin[1] + dy)
        # if draw:
        self._draw()
        if self.on_drag_move is not None:
            self.call_on_drag_move({'event': event, 'artist': self._grab_artist})
        if self.on_change is not None:
            self.call_on_change(self._grab_artist.parent)
        # super()._move_line(event=event, draw=False)
        # self._grab_artist._fill.set_xy(np.array(self._grab_artist.get_data()).T)
        # self._draw()

    def _release_polygon(self, event: Event, kind: str):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        self._pick_lock = False
        if (kind == 'vertex') and (self.on_vertex_release is not None):
            self.call_on_vertex_release({
                'event': event,
                'ind': self._moving_vertex_index,
                'artist': self._moving_vertex_artist
            })
        elif (kind == 'drag') and (self.on_drag_release is not None):
            self.call_on_drag_release({'event': event, 'artist': self._grab_artist})
