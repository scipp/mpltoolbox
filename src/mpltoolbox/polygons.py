# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from .utils import make_color
import numpy as np
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from matplotlib.patches import Polygon


class Polygons(Tool):

    def __init__(self, ax: Axes, alpha=0.05, **kwargs):
        super().__init__(ax, **kwargs)
        self.lines = []
        self._pick_lock = False
        self._moving_vertex_index = None
        self._moving_vertex_artist = None
        self._color = color
        self._line_counter = 0
        self._distance_from_first_point = 0.05
        self._first_point_position = None
        self._finalize_polygon = False
        self._alpha = alpha

    def __del__(self):
        super().shutdown(artists=self.lines + [line._fill for line in self.lines])

    def _make_new_line(self, x: float, y: float):
        # super()._make_new_line(x=x, y=y)
        line, = self._ax.plot([x, x], [y, y],
                              '-o',
                              color=make_color(color=self._color,
                                               counter=self._line_counter))
        self.lines.append(line)
        self._line_counter += 1
        self._first_point_position_data = (x, y)
        self._first_point_position_axes = self._data_to_axes_transform(x, y)
        fill, = self._ax.fill(line.get_xdata(),
                              line.get_ydata(),
                              color=line.get_color(),
                              alpha=self._alpha)
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

    def _after_line_creation(self, event):
        # self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
        #     'motion_notify_event', self._on_motion_notify)
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
            # self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
            # del self._connections['motion_notify_event']
            self._disconnect(['motion_notify_event'])
            self._finalize_line(event)
            self._finalize_polygon = False
        else:
            self._duplicate_last_vertex()
            # new_data = self.lines[-1].get_data()
            # self.lines[-1].set_data(
            #     (np.append(new_data[0],
            #                new_data[0][-1]), np.append(new_data[1], new_data[1][-1])))
            # self._draw()

    def _finalize_line(self, event):
        self.lines[-1].set_picker(5.0)
        self.lines[-1]._fill.set_picker(5.0)
        if self.on_create is not None:
            self.on_create(event)
        self._draw()

    def _remove_line(self, line: Artist):
        if isinstance(line, Polygon):
            line = line._line
        line._fill.remove()
        line.remove()
        self.lines.remove(line)
        self._draw()

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

    def _grab_line(self, event: Event):
        if isinstance(event.artist, Polygon):
            event.artist = event.artist._line
        super()._grab_line(event)
        # # self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
        # #     'motion_notify_event', self._move_line)
        # # self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
        # #     'button_release_event', partial(self._release_line, kind='grab'))
        # self._connect({
        #     'motion_notify_event': self._move_line,
        #     'button_release_event': partial(self._release_line, kind='grab')
        # })

        # self._grab_artist = event.artist
        # self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        # self._grab_artist_origin = self._grab_artist.get_data()

    def _move_line(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        new_data = (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy)
        self._grab_artist.set_data(new_data)
        self._grab_artist._fill.set_xy(np.array(new_data).T)
        self._draw()
