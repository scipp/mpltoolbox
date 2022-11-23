# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .tool import Tool
from functools import partial
from matplotlib.patches import Polygon
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event
from matplotlib.colors import to_rgb
import uuid


class HSpan:

    def __init__(self, x: float, y: float, ax: Axes, **kwargs):

        # vertical = span == 'axvspan'
        # arg = x if vertical else y
        self._ax = ax
        self._span = self._ax.axvspan(x, x, **kwargs)
        self._vertices = None
        self._span.parent = self

    @property
    def left(self):
        return self._span.get_xy()[0, 0]
        # return min(corners[0, 0], corners[2, 0])

    @left.setter
    def left(self, x):
        corners = self._span.get_xy()
        for i in [0, 1]:
            corners[i, 0] = x
        if len(corners) > 3:
            corners[4, 0] = x
        else:
            corners += [x, corners[0, 1]]
        self._span.set_xy(corners)
        if self._vertices is not None:
            self._vertices.set_xdata([corners[0, 0], corners[2, 0]])

    @property
    def right(self):
        return self._span.get_xy()[2, 0]

    @right.setter
    def right(self, x):
        corners = self._span.get_xy()
        for i in [2, 3]:
            corners[i, 0] = x
        self._span.set_xy(corners)
        if self._vertices is not None:
            self._vertices.set_xdata([corners[0, 0], corners[2, 0]])

    @property
    def color(self):
        return self._span.get_edgecolor()

    def remove(self):
        self._span.remove()
        self._vertices.remove()

    def add_vertices(self):
        self._vertices, = self._ax.plot([self.left, self.right], [0.5, 0.5],
                                        'o',
                                        ls='None',
                                        mec=self.color,
                                        mfc='None',
                                        picker=5.0,
                                        transform=self._span.get_transform())
        self._vertices.parent = self
        # span._vertices = line
        # line._span = span


class Spans(Tool):

    def __init__(self, ax: Axes, span: HSpan, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._span = span
        self.spans = []
        # self._drag_span = False
        # self._grab_artist = None
        # self._grab_mouse_origin = None
        # self._grab_artist_origin = None
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
        # arg = x if self._span == 'axvspan' else y
        span = self._span(x, y, ax=self._ax, picker=True, **kwargs)
        span.id = str(uuid.uuid1())
        self.spans.append(span)
        self._artist_counter += 1
        self._draw()

    def _persist_span(self, event: Event = None):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        if event is not None:
            # self._add_vertices()
            self.spans[-1].add_vertices()
            self._draw()
            if self.on_create is not None:
                self.on_create({'event': event, 'artist': self.spans[-1]})


# def _add_vertices(self):
#         # span = self.spans[-1]
#         # line, = self._ax.plot([span.left, span.right], [0.5, 0.5],
#         #                       'o',
#         #                       ls='None',
#         #                       mec=span.color,
#         #                       mfc='None',
#         #                       picker=5.0,
#         #                       transform=span._span.get_transform())
#         # # line, = self._ax.plot(vertices[0],
#         # #                       vertices[1],
#         # #                       'o',
#         # #                       mec=span.get_edgecolor(),
#         # #                       mfc='None',
#         # #                       picker=5.0)
#         # span._vertices = line
#         # line._span = span
#         self.spans[-1].add_vertices()

    def _remove_span(self, span: Artist):
        span.parent.remove()
        # span._vertices.remove()
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


class Vspans(Spans):

    def __init__(self, ax: Axes, **kwargs):
        super().__init__(ax=ax, span=HSpan, **kwargs)

    def _resize_span(self, event: Event):
        if event.inaxes != self._ax:
            return

        self.spans[-1].right = event.xdata
        # for i in [2, 3]:
        #     corners[i, 0] = event.xdata
        # self.spans[-1].set_xy(corners)
        self._draw()

    def _grab_span(self, event: Event):
        super()._grab_span(event)
        self._grab_artist_origin = [
            self._grab_artist.parent.left, self._grab_artist.parent.right
        ]

    def _update_artist_position(self, dx, dy):
        span = self._grab_artist.parent
        span.right = self._grab_artist_origin[0] + dx
        span.left = self._grab_artist_origin[1] + dx
