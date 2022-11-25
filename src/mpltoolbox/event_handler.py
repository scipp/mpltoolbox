# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from functools import partial
from matplotlib.patches import Patch
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb
import uuid


class EventHandler(Tool):

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._maker = None
        self.artists = []
        self._drag_patch = False
        self._grab_artist = None
        self._grab_mouse_origin = None
        self._grab_artist_origin = None
        self._pick_lock = False
        self._nclicks = 0

    def __del__(self):
        super().shutdown(artists=self.artists)

    def _on_button_press(self, event: Event):
        # if event.button != 1 or self._pick_lock or self._get_active_tool():
        #     return
        # if event.inaxes != self._ax:
        #     return
        # self._make_new_patch(x=event.xdata, y=event.ydata)
        # self._connect({
        #     'motion_notify_event': self._resize_patch,
        #     'button_release_event': self._persist_patch
        # })
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        if 'motion_notify_event' not in self._connections:
            self._nclicks = 0
            self._make_new_artist(x=event.xdata, y=event.ydata)
            self._connect({'motion_notify_event': self._on_motion_notify})
        self._nclicks += 1
        self._persist_vertex(event)

    def _make_new_artist(self, x: float, y: float):
        # kwargs = self._parse_kwargs()
        # defaut_color = f'C{self._artist_counter}'
        # if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
        #     kwargs['ec'] = defaut_color
        # if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
        #     kwargs['fc'] = to_rgb(defaut_color) + (0.05, )
        artist = self._maker(x=x,
                             y=y,
                             number=self._artist_counter,
                             ax=self._ax,
                             **self._kwargs)
        # patch.id = str(uuid.uuid1())
        self.artists.append(artist)
        self._artist_counter += 1
        # self._ax.add_patch(patch)
        self._draw()

    def _on_motion_notify(self, event: Event):
        self._move_vertex(event=event, ind=None, artist=self.artists[-1])

    def _persist_vertex(self, event: Event = None):
        # if len(self.lines[-1]) == self._nclicks:
        print(self._nclicks, self._max_clicks)
        if self._nclicks == self._max_clicks:
            self._disconnect(['motion_notify_event'])
            self._finalize_artist(event)

        # self._disconnect(['motion_notify_event', 'button_release_event'])
        # if event is not None:
        #     self.artists[-1].add_vertices()
        #     self._draw()
        #     if self.on_create is not None:
        #         self.call_on_create({'event': event, 'artist': self.artists[-1]})

    def _finalize_artist(self, event: Event):
        self.artists[-1].set_picker(5.0)
        if self.on_create is not None:
            self.call_on_create({'event': event, 'artist': self.artists[-1]})
        self._draw()

    def _remove_patch(self, patch: Artist):
        patch.parent.remove()
        # patch._vertices.remove()
        self.artists.remove(patch.parent)
        self._draw()

    def _on_pick(self, event: Event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        # is_patch = isinstance(event.artist, Patch)
        art = event.artist
        if event.mouseevent.button == 1:
            if not art.parent.is_moveable(art):
                return
            self._pick_lock = True
            self._grab_vertex(event)
            if self.on_vertex_press is not None:
                self.call_on_vertex_press({
                    'event': event,
                    'ind': self._moving_vertex_index,
                    'artist': self._moving_vertex_artist
                })
        if event.mouseevent.button == 3:
            if art.parent.is_draggable(art):
                return
            self._pick_lock = True
            self._grab_patch(event)
            if self.on_drag_press is not None:
                self.call_on_drag_press({'event': event, 'artist': self._grab_artist})
        elif event.mouseevent.button == 2:
            if art.parent.is_removable(art):
                return
            self._remove_patch(event.artist)
            if self.on_remove is not None:
                self.call_on_remove({'event': event, 'artist': event.artist})

    def _grab_vertex(self, event: Event):
        self._connect({
            'motion_notify_event': self._on_vertex_motion,
            'button_release_event': partial(self._release, kind='vertex')
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
            self.call_on_drag_move({'event': event, 'artist': self._grab_artist})
        if self.on_change is not None:
            self.call_on_change(self._grab_artist.parent)

    def _release_patch(self, event: Event, kind: str):
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
