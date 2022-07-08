# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)


class Tool:

    def __init__(self,
                 ax,
                 *,
                 autostart=True,
                 on_vertex_press=None,
                 on_vertex_move=None,
                 on_vertex_release=None,
                 on_drag_press=None,
                 on_drag_move=None,
                 on_drag_release=None):

        self._ax = ax
        self._fig = ax.get_figure()
        self._connections = {}

        self.on_vertex_press = on_vertex_press
        self.on_vertex_move = on_vertex_move
        self.on_vertex_release = on_vertex_release
        self.on_drag_press = on_drag_press
        self.on_drag_move = on_drag_move
        self.on_drag_release = on_drag_release

        if autostart:
            self.start()

    def start(self):
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

    def stop(self):
        for c in self._connections.values():
            self._fig.canvas.mpl_disconnect(c)

    def shutdown(self, artists):
        self.stop()
        for a in artists:
            a.remove()
        del artists, self._connections
        self._fig.canvas.draw_idle()
