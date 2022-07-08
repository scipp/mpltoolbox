# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
import numpy as np


class Points(Tool):

    def __init__(self, ax, color=None, **kwargs):

        super().__init__(ax, **kwargs)

        self._scatter = None
        self._pick_lock = False
        self._moving_dot_indices = None

    def __del__(self):
        super().shutdown(artists=[self._scatter])

    def _make_scatter(self, x=0, y=0):
        self._scatter = self._ax.scatter([x], [y], picker=True)
        self._fig.canvas.draw_idle()

    def _on_button_press(self, event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        x, y = event.xdata, event.ydata
        # if None in (x, y):
        #     return
        if self._scatter is None:
            self._make_scatter(x=x, y=y)
        else:
            self._persist_dot(x=x, y=y)
        # if self.on_button_press is not None:
        #     self.on_button_press(event)

    def _persist_dot(self, x, y):
        offsets = self._scatter.get_offsets()
        offsets = np.concatenate([offsets, [[x, y]]])
        self._scatter.set_offsets(offsets)
        self._fig.canvas.draw_idle()

    def _remove_point(self, inds):
        offsets = np.delete(self._scatter.get_offsets(), inds, axis=0)
        self._scatter.set_offsets(offsets)
        self._fig.canvas.draw_idle()

    def _on_pick(self, event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        button = event.mouseevent.button
        if button == 1:
            self._pick_lock = True
            self._activate_moving_dot(event)
        elif button in (2, 3):
            self._remove_point(event.ind)
        # if self.on_pick is not None:
        #     self.on_pick(event)

    def _activate_moving_dot(self, event):
        self._connections['motion_notify_event'] = self._fig.canvas.mpl_connect(
            'motion_notify_event', self._on_motion_notify)
        self._connections['button_release_event'] = self._fig.canvas.mpl_connect(
            'button_release_event', self._on_button_release)
        self._moving_dot_indices = event.ind

    def _on_motion_notify(self, event):
        self._move_dot(event)
        # if self.on_motion_notify is not None:
        #     self.on_motion_notify(event)

    def _move_dot(self, event):
        if event.inaxes != self._ax:
            return
        ind = self._moving_dot_indices[0]
        offsets = self._scatter.get_offsets()
        offsets[ind] = [event.xdata, event.ydata]
        self._scatter.set_offsets(offsets)
        self._fig.canvas.draw_idle()

    def _on_button_release(self, event):
        self._fig.canvas.mpl_disconnect(self._connections['motion_notify_event'])
        self._fig.canvas.mpl_disconnect(self._connections['button_release_event'])
        self._pick_lock = False

    def get_points(self):
        return self._scatter.get_offsets()
