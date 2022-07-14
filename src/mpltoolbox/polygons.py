# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from matplotlib.patches import Polygon


class Polygons(Tool):
    """
    Add closed polygons to the supplied axes.

    Controls:
      - Left-click to make new polygons
      - Left-click and hold on polygon vertex to move vertex
      - Right-click and hold to drag/move the entire polygon
      - Middle-click to delete polygon

    :param ax: The Matplotlib axes to which the Lines tool will be attached.
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
        self.lines = []
        self._pick_lock = False
        self._moving_vertex_index = None
        self._moving_vertex_artist = None
        self._distance_from_first_point = 0.05
        self._first_point_position = None
        self._finalize_polygon = False

    def __del__(self):
        super().shutdown(artists=self.lines + [line._fill for line in self.lines])

    def _make_new_line(self, x: float, y: float):
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
        line, = self._ax.plot([x, x], [y, y], '-o', **line_kwargs)
        self.lines.append(line)
        self._artist_counter += 1
        self._first_point_position_data = (x, y)
        self._first_point_position_axes = self._data_to_axes_transform(x, y)
        if 'alpha' not in fill_kwargs:
            fill_kwargs['alpha'] = 0.05
        if set(['fc', 'facecolor']).isdisjoint(set(fill_kwargs.keys())):
            fill_kwargs['fc'] = line.get_color()
        fill, = self._ax.fill(line.get_xdata(), line.get_ydata(), **fill_kwargs)
        line._fill = fill
        fill._line = line

    def _data_to_axes_transform(self, x, y):
        trans = self._ax.transData.transform((x, y))
        return self._ax.transAxes.inverted().transform(trans)

    def _compute_distance_from_first_point(self, event):
        xdisplay, ydisplay = self._data_to_axes_transform(event.xdata, event.ydata)
        dist = np.sqrt((xdisplay - self._first_point_position_axes[0])**2 +
                       (ydisplay - self._first_point_position_axes[1])**2)
        return dist

    def _on_motion_notify(self, event: Event):
        if self._compute_distance_from_first_point(
                event) < self._distance_from_first_point:
            event.xdata = self._first_point_position_data[0]
            event.ydata = self._first_point_position_data[1]
            self._finalize_polygon = True
        else:
            self._finalize_polygon = False
        self._move_vertex(event=event, ind=-1, line=self.lines[-1])

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
        if self._finalize_polygon:
            self._disconnect(['motion_notify_event'])
            self._finalize_line(event)
            self._finalize_polygon = False
        else:
            self._duplicate_last_vertex()

    def _finalize_line(self, event: Event):
        self.lines[-1].set_picker(5.0)
        self.lines[-1]._fill.set_picker(5.0)
        if self.on_create is not None:
            self.on_create(event)
        self._draw()

    def _remove_polygon(self, artist: Artist):
        artist.remove()
        artist._line.remove()
        self.lines.remove(artist._line)
        self._draw()

    def _on_pick(self, event: Event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        is_polygon = isinstance(event.artist, Polygon)
        if event.mouseevent.button == 1:
            if is_polygon:
                return
            self._pick_lock = True
            self._grab_vertex(event)
            if self.on_vertex_press is not None:
                self.on_vertex_press(event)
        elif event.mouseevent.button == 2:
            if not is_polygon:
                return
            self._remove_polygon(event.artist)
            if self.on_remove is not None:
                self.on_remove(event)
        elif event.mouseevent.button == 3:
            if not is_polygon:
                return
            self._pick_lock = True
            self._grab_polygon(event)
            if self.on_drag_press is not None:
                self.on_drag_press(event)

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
        self._move_vertex(event=event,
                          ind=self._moving_vertex_index,
                          line=self._moving_vertex_artist)
        if self.on_vertex_move is not None:
            self.on_vertex_move(event)

    def _move_vertex(self, event: Event, ind: int, line: Artist):
        if event.inaxes != self._ax:
            return
        new_data = line.get_data()
        if ind in (0, len(new_data[0])):
            ind = [0, -1]
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        line.set_data(new_data)
        line._fill.set_xy(np.array(new_data).T)
        self._draw()

    def _grab_polygon(self, event: Event):
        self._connect({
            'motion_notify_event':
            self._move_polygon,
            'button_release_event':
            partial(self._release_polygon, kind='grab')
        })
        self._grab_artist = event.artist._line
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grab_artist_origin = self._grab_artist.get_data()

    def _move_polygon(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        new_data = (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy)
        self._grab_artist.set_data(new_data)
        self._grab_artist._fill.set_xy(np.array(new_data).T)
        self._draw()

    def _release_polygon(self, event: Event, kind: str):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        self._pick_lock = False
        if (kind == 'vertex') and (self.on_vertex_release is not None):
            self.on_vertex_release(event)
        elif (kind == 'drag') and (self.on_drag_release is not None):
            self.on_drag_release(event)
