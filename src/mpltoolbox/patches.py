# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from functools import partial
from matplotlib.patches import Patch
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb
import uuid


class Patches(Tool):

    def __init__(self, ax: Axes, patch: Patch, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._patch = patch
        self.patches = []
        self._drag_patch = False
        self._grab_artist = None
        self._grab_mouse_origin = None
        self._grab_artist_origin = None
        self._pick_lock = False

    def __del__(self):
        super().shutdown(artists=self.patches)

    def _on_button_press(self, event: Event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        self._make_new_patch(x=event.xdata, y=event.ydata)
        self._connect({
            'motion_notify_event': self._resize_patch,
            'button_release_event': self._persist_patch
        })

    def _make_new_patch(self, x: float, y: float):
        kwargs = self._parse_kwargs()
        defaut_color = f'C{self._artist_counter}'
        if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['ec'] = defaut_color
        if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['fc'] = to_rgb(defaut_color) + (0.05, )
        patch = self._patch((x, y), 0, 0, picker=True, **kwargs)
        patch.id = str(uuid.uuid1())
        self.patches.append(patch)
        self._artist_counter += 1
        self._ax.add_patch(patch)
        self._draw()

    def _persist_patch(self, event: Event = None):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        if event is not None:
            self._add_vertices()
            self._draw()
            if self.on_create is not None:
                self.on_create({'event': event, 'artist': self.patches[-1]})

    def _remove_patch(self, patch: Artist):
        patch.remove()
        patch._vertices.remove()
        self.patches.remove(patch)
        self._draw()

    def _on_pick(self, event: Event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        is_patch = isinstance(event.artist, Patch)
        if event.mouseevent.button == 1:
            if is_patch:
                return
            self._pick_lock = True
            self._grab_vertex(event)
            if self.on_vertex_press is not None:
                self.on_vertex_press({
                    'event': event,
                    'ind': self._moving_vertex_index,
                    'artist': self._moving_vertex_artist
                })
        if event.mouseevent.button == 3:
            if not is_patch:
                return
            self._pick_lock = True
            self._grab_patch(event)
            if self.on_drag_press is not None:
                self.on_drag_press({'event': event, 'artist': self._grab_artist})
        elif event.mouseevent.button == 2:
            if not is_patch:
                return
            self._remove_patch(event.artist)
            if self.on_remove is not None:
                self.on_remove({'event': event, 'artist': event.artist})

    def _grab_vertex(self, event: Event):
        self._connect({
            'motion_notify_event':
            self._on_vertex_motion,
            'button_release_event':
            partial(self._release_patch, kind='vertex')
        })

        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_artist = event.artist

    def _on_vertex_motion(self, event: Event):
        self._move_vertex(event=event,
                          ind=self._moving_vertex_index,
                          line=self._moving_vertex_artist)
        if self.on_vertex_move is not None:
            self.on_vertex_move({
                'event': event,
                'ind': self._moving_vertex_index,
                'artist': self._moving_vertex_artist
            })

    def _grab_patch(self, event: Event):
        self._connect({
            'motion_notify_event': self._move_patch,
            'button_release_event': partial(self._release_patch, kind='drag')
        })
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
            self.on_drag_move({'event': event, 'artist': self._grab_artist})

    def _release_patch(self, event: Event, kind: str):
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
