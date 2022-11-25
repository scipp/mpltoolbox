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

    def __init__(self, ax: Axes, spawner, **kwargs):
        super().__init__(ax=ax, **kwargs)
        self._spawner = spawner
        self.children = []
        self._drag_patch = False
        self._grabbed_child = None
        self._grab_mouse_origin = None
        self._grabbed_artist_origin = None
        self._pick_lock = False
        self._nclicks = 0

    def __del__(self):
        super().shutdown(children=self.children)

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
            self._spawn_new_motif(x=event.xdata, y=event.ydata)
            self._connect({'motion_notify_event': self._on_motion_notify})
        self._nclicks += 1
        self._persist_vertex(event=event, motif=self.children[-1])

    def _spawn_new_motif(self, x: float, y: float):
        # kwargs = self._parse_kwargs()
        # defaut_color = f'C{self._artist_counter}'
        # if set(['ec', 'edgecolor']).isdisjoint(set(kwargs.keys())):
        #     kwargs['ec'] = defaut_color
        # if set(['fc', 'facecolor']).isdisjoint(set(kwargs.keys())):
        #     kwargs['fc'] = to_rgb(defaut_color) + (0.05, )
        motif = self._spawner(x=x,
                              y=y,
                              number=self._motif_counter,
                              ax=self._ax,
                              **self._kwargs)
        # patch.id = str(uuid.uuid1())
        self.children.append(motif)
        self._motif_counter += 1
        # self._ax.add_patch(patch)
        self._draw()

    def _on_motion_notify(self, event: Event):
        self._move_vertex(event=event, ind=None, motif=self.children[-1])

    def _move_vertex(self, event: Event, ind: int, motif):
        if event.inaxes != self._ax:
            return
        motif.move_vertex(event=event, ind=ind)

    def _persist_vertex(self, event: Event, motif):
        # if len(self.lines[-1]) == self._nclicks:
        # print(self._nclicks, self._max_clicks)
        if self._nclicks == motif._max_clicks:
            self._disconnect(['motion_notify_event'])
            self._finalize_motif(event)
        else:
            motif.after_persist_vertex(event)
        self._draw()

        # self._disconnect(['motion_notify_event', 'button_release_event'])
        # if event is not None:
        #     self.artists[-1].add_vertices()
        #     self._draw()
        #     if self.on_create is not None:
        #         self.call_on_create({'event': event, 'artist': self.artists[-1]})

    def _finalize_motif(self, event: Event):
        self.children[-1].set_picker(5.0)
        if self.on_create is not None:
            self.call_on_create({'event': event, 'owner': self.children[-1]})
        # self._draw()

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
                    'motif': self._moving_vertex_motif
                })
        if event.mouseevent.button == 3:
            if not art.parent.is_draggable(art):
                return
            self._pick_lock = True
            self._grab_motif(event)
            if self.on_drag_press is not None:
                self.call_on_drag_press({'event': event, 'motif': self._grabbed_motif})
        elif event.mouseevent.button == 2:
            if not art.parent.is_removable(art):
                return
            self._remove_motif(art.parent)
            if self.on_remove is not None:
                self.call_on_remove({'event': event, 'motif': art.parent})

    def _remove_motif(self, motif):
        motif.remove()
        self.children.remove(motif)
        self._draw()

    def _grab_vertex(self, event: Event):
        self._connect({
            'motion_notify_event':
            self._on_vertex_motion,
            'button_release_event':
            partial(self._release_motif, kind='vertex')
        })

        self._moving_vertex_index = event.ind[0]
        self._moving_vertex_motif = event.artist.parent

    def _on_vertex_motion(self, event: Event):
        event_dict = {
            'event': event,
            'ind': self._moving_vertex_index,
            'motif': self._moving_vertex_motif
        }
        self._move_vertex(**event_dict)
        self._draw()
        if self.on_vertex_move is not None:
            self.call_on_vertex_move(event_dict)
        if self.on_change is not None:
            self.call_on_change(self._moving_vertex_motif)

    def _grab_motif(self, event: Event):
        self._connect({
            'motion_notify_event': self._move_motif,
            'button_release_event': partial(self._release_motif, kind='drag')
        })
        self._grabbed_motif = event.artist.parent
        self._grab_mouse_origin = event.mouseevent.xdata, event.mouseevent.ydata
        self._grabbed_motif_origin = self._grabbed_motif.xy

    def _move_motif(self, event: Event):
        if event.inaxes != self._ax:
            return
        dx = event.xdata - self._grab_mouse_origin[0]
        dy = event.ydata - self._grab_mouse_origin[1]
        # self._update_motif_position(dx, dy)
        self._grabbed_motif.xy = (self._grabbed_motif_origin[0] + dx,
                                  self._grabbed_motif_origin[1] + dy)
        self._draw()
        if self.on_drag_move is not None:
            self.call_on_drag_move({'event': event, 'motif': self._grabbed_motif})
        if self.on_change is not None:
            self.call_on_change(self._grabbed_motif)

    def _release_motif(self, event: Event, kind: str):
        self._disconnect(['motion_notify_event', 'button_release_event'])
        self._pick_lock = False
        if (kind == 'vertex') and (self.on_vertex_release is not None):
            self.call_on_vertex_release({
                'event': event,
                'ind': self._moving_vertex_index,
                'motif': self._moving_vertex_motif
            })
        elif (kind == 'drag') and (self.on_drag_release is not None):
            self.call_on_drag_release({'event': event, 'motif': self._grabbed_motif})
