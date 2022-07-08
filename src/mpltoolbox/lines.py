# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
import numpy as np


class Lines(Tool):

    def __init__(self, ax, n, **kwargs):

        super().__init__(ax, **kwargs)

        self._nmax = n
        self.lines = []
        self._pick_lock = False
        self._moving_vertex_index = None
        self._moving_vertex_artist = None

    def __del__(self):
        super().shutdown(artists=self.lines)

    def _make_new_line(self, x=0, y=0):
        # line = Line(ax=self._ax, x=x, y=y)
        line = self._ax.plot([x, x], [y, y], '-o')[0]
        self.lines.append(line)

    def _on_motion_notify(self, event):
        # self._move_dot(event)
        self._move_vertex(event=event, ind=-1, line=self.lines[-1])
        # if self.on_motion_notify is not None:
        #     self.on_motion_notify(event)

    def _on_button_press(self, event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        # if None in (event.xdata, event.ydata):
        if event.inaxes != self._ax:
            return
        # if not self._active_line_drawing:
        if 'motion_notify_event' not in self._connections:
            self._make_new_line(x=event.xdata, y=event.ydata)
            # self._active_line_drawing = True
            self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
                'motion_notify_event', self._on_motion_notify)
            self._fig.canvas.draw_idle()
        else:
            self._persist_dot(event)
        # if self.on_button_press is not None:
        #     self.on_button_press(event)

    def _persist_dot(self, event):
        # if None in (event.xdata, event.ydata):
        #     return
        if self._get_line_length(-1) == self._nmax:
            # self._active_line_drawing = False
            self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
            del self._connections['motion_notify_event']
            self.lines[-1].set_picker(5.0)
        else:
            new_data = self.lines[-1].get_data()
            self.lines[-1].set_data(
                (np.append(new_data[0],
                           new_data[0][-1]), np.append(new_data[1], new_data[1][-1])))
        self._fig.canvas.draw_idle()

    def _remove_line(self, line):
        line.remove()
        self.lines.remove(line)
        self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        if event.mouseevent.button == 1:
            self._pick_lock = True
            self._grab_vertex(event)
        elif event.mouseevent.button == 2:
            self._remove_line(event.artist)
        elif event.mouseevent.button == 3:
            self._pick_lock = True
            self._grab_line(event)

    def _grab_vertex(self, event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_vertex_motion)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._release_line)
        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_artist = event.artist

    def _on_vertex_motion(self, event):
        self._move_vertex(event=event,
                          ind=self._moving_vertex_index,
                          line=self._moving_vertex_artist)

    def _move_vertex(self, event, ind, line):
        # if None in (event.xdata, event.ydata):
        #     return
        if event.inaxes != self._ax:
            return
        # ind = self._moving_vertex_index
        # line = self._moving_vertex_artist
        new_data = line.get_data()
        new_data[0][ind] = event.xdata
        new_data[1][ind] = event.ydata
        line.set_data(new_data)
        self._fig.canvas.draw_idle()

        # if self.on_pick is not None:
        #     self.on_pick(event)

    def _release_line(self, event):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        del self._connections['motion_notify_event']
        del self._connections['button_release_event']
        self._pick_lock = False

    def _grab_line(self, event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._move_line)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._release_line)
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grab_artist_origin = self._grab_artist.get_data()

    def _move_line(self, event):
        # if None in (event.xdata, event.ydata):
        #     return
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._grab_artist.set_data(
            (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy))
        self._fig.canvas.draw_idle()

    def _get_line_length(self, ind):
        return len(self.lines[ind].get_xydata())

    def get_line(self, ind):
        return self.lines[ind].get_xydata()
