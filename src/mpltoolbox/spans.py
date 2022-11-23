# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from functools import partial
from matplotlib.patches import Polygon
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb
import uuid


class Spans(Tool):

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._span = None
        self.spans = []
        self._grab_artist = None
        self._grab_mouse_origin = None
        self._grab_artist_origin = None
        self._pick_lock = False

    def __del__(self):
        super().shutdown(artists=self.spans)

    def _on_button_press(self, event: Event):
        if event.button != 1 or self._pick_lock or self._get_active_tool():
            return
        if event.inaxes != self._ax:
            return
        self._make_new_span(x=event.xdata, y=event.ydata)
        self._connect({
            'motion_notify_event': self._resize_span,
            'button_release_event': self._persist_span
        })

    def _make_new_span(self, x: float, y: float):
        kwargs = self._parse_kwargs()
        defaut_color = f'C{self._artist_counter}'
        if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['ec'] = defaut_color
        if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
            kwargs['fc'] = to_rgb(defaut_color) + (0.1, )
        span = self._span(x, y, ax=self._ax, picker=True, **kwargs)
        span.id = str(uuid.uuid1())
        self.spans.append(span)
        self._artist_counter += 1
        self._draw()

    def _persist_span(self, event: Event = None):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        if event is not None:
            self.spans[-1].add_vertices()
            self._draw()
            if self.on_create is not None:
                self.on_create({'event': event, 'artist': self.spans[-1]})

    def _remove_span(self, span: Artist):
        span.parent.remove()
        self.spans.remove(span.parent)
        self._draw()

    def _on_pick(self, event: Event):
        if self._get_active_tool():
            return
        if event.mouseevent.inaxes != self._ax:
            return
        is_span = isinstance(event.artist, Polygon)
        if event.mouseevent.button == 1:
            if is_span:
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
            if not is_span:
                return
            self._pick_lock = True
            self._grab_span(event)
            if self.on_drag_press is not None:
                self.on_drag_press({'event': event, 'artist': self._grab_artist})
        elif event.mouseevent.button == 2:
            if not is_span:
                return
            self._remove_span(event.artist)
            if self.on_remove is not None:
                self.on_remove({'event': event, 'artist': event.artist})

    def _grab_vertex(self, event: Event):
        self._connect({
            'motion_notify_event': self._on_vertex_motion,
            'button_release_event': partial(self._release_span, kind='vertex')
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

    def _grab_span(self, event: Event):
        self._connect({
            'motion_notify_event': self._move_span,
            'button_release_event': partial(self._release_span, kind='drag')
        })
        self._grab_artist = event.artist
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata

    def _move_span(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        self._update_artist_position(dx, dy)
        self._draw()
        if self.on_drag_move is not None:
            self.on_drag_move({'event': event, 'artist': self._grab_artist})

    def _release_span(self, event: Event, kind: str):
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
