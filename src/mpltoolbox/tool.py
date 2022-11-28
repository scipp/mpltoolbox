# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)
from functools import partial
from matplotlib.pyplot import Artist, Axes
from matplotlib.backend_bases import Event
from typing import Callable, List


class Tool:

    def __init__(self,
                 ax: Axes,
                 spawner,
                 *,
                 autostart: bool = True,
                 on_create: Callable = None,
                 on_remove: Callable = None,
                 on_change: Callable = None,
                 on_vertex_press: Callable = None,
                 on_vertex_move: Callable = None,
                 on_vertex_release: Callable = None,
                 on_drag_press: Callable = None,
                 on_drag_move: Callable = None,
                 on_drag_release: Callable = None,
                 **kwargs):
        self._ax = ax
        self._fig = ax.get_figure()
        self._connections = {}

        self._on_create = []
        self._on_remove = []
        self._on_change = []
        self._on_vertex_press = []
        self._on_vertex_move = []
        self._on_vertex_release = []
        self._on_drag_press = []
        self._on_drag_move = []
        self._on_drag_release = []

        self.on_create = on_create
        self.on_remove = on_remove
        self.on_change = on_change
        self.on_vertex_press = on_vertex_press
        self.on_vertex_move = on_vertex_move
        self.on_vertex_release = on_vertex_release
        self.on_drag_press = on_drag_press
        self.on_drag_move = on_drag_move
        self.on_drag_release = on_drag_release

        self._kwargs = kwargs
        self._motif_counter = 0

        self._spawner = spawner
        self.children = []
        self._drag_patch = False
        self._grabbed_child = None
        self._grab_mouse_origin = None
        self._grabbed_artist_origin = None
        self._pick_lock = False
        self._nclicks = 0

        if autostart:
            self.start()

    def __del__(self):
        self.shutdown()

    @property
    def on_create(self):
        return self._on_create

    @on_create.setter
    def on_create(self, func: Callable):
        if func is not None:
            self._on_create.append(func)

    def call_on_create(self, event):
        for func in self._on_create:
            func(event)

    @property
    def on_remove(self):
        return self._on_remove

    @on_remove.setter
    def on_remove(self, func: Callable):
        if func is not None:
            self._on_remove.append(func)

    def call_on_remove(self, event):
        for func in self._on_remove:
            func(event)

    @property
    def on_change(self):
        return self._on_change

    @on_change.setter
    def on_change(self, func: Callable):
        if func is not None:
            self._on_change.append(func)

    def call_on_change(self, event):
        for func in self._on_change:
            func(event)

    @property
    def on_vertex_press(self):
        return self._on_vertex_press

    @on_vertex_press.setter
    def on_vertex_press(self, func: Callable):
        if func is not None:
            self._on_vertex_press.append(func)

    def call_on_vertex_press(self, event):
        for func in self._on_vertex_press:
            func(event)

    @property
    def on_vertex_move(self):
        return self._on_vertex_move

    @on_vertex_move.setter
    def on_vertex_move(self, func: Callable):
        if func is not None:
            self._on_vertex_move.append(func)

    def call_on_vertex_move(self, event):
        for func in self._on_vertex_move:
            func(event)

    @property
    def on_vertex_release(self):
        return self._on_vertex_release

    @on_vertex_release.setter
    def on_vertex_release(self, func: Callable):
        if func is not None:
            self._on_vertex_release.append(func)

    def call_on_vertex_release(self, event):
        for func in self._on_vertex_release:
            func(event)

    @property
    def on_drag_press(self):
        return self._on_drag_press

    @on_drag_press.setter
    def on_drag_press(self, func: Callable):
        if func is not None:
            self._on_drag_press.append(func)

    def call_on_drag_press(self, event):
        for func in self._on_drag_press:
            func(event)

    @property
    def on_drag_move(self):
        return self._on_drag_move

    @on_drag_move.setter
    def on_drag_move(self, func: Callable):
        if func is not None:
            self._on_drag_move.append(func)

    def call_on_drag_move(self, event):
        for func in self._on_drag_move:
            func(event)

    @property
    def on_drag_release(self):
        return self._on_drag_release

    @on_drag_release.setter
    def on_drag_release(self, func: Callable):
        if func is not None:
            self._on_drag_release.append(func)

    def call_on_drag_release(self, event):
        for func in self._on_drag_release:
            func(event)

    def _parse_kwargs(self):
        parsed = {}
        for key, value in self._kwargs.items():
            if callable(value):
                parsed[key] = value()
            elif isinstance(value, list):
                parsed[key] = value[self._artist_counter % len(value)]
            else:
                parsed[key] = value
        return parsed

    def _draw(self):
        self._fig.canvas.draw_idle()

    def start(self):
        """
        Activate the tool.
        """
        self._connections['button_press_event'] = self._fig.canvas.mpl_connect(
            'button_press_event', self._on_button_press)
        self._connections['pick_event'] = self._fig.canvas.mpl_connect(
            'pick_event', self._on_pick)

    def stop(self):
        """
        Dectivate the tool.
        """
        self._disconnect(list(self._connections.keys()))

    def shutdown(self):
        """
        Deactivate the tool and remove all children from the axes.
        """
        self.stop()
        for a in self.children:
            a.remove()
        self.children.clear()
        self._connections.clear()
        self._draw()

    def _get_active_tool(self) -> str:
        return self._fig.canvas.toolbar.mode

    def _disconnect(self, keys: List[str]):
        for key in keys:
            if key in self._connections:
                self._fig.canvas.mpl_disconnect(self._connections[key])
                del self._connections[key]

    def _connect(self, connections: dict):
        for key, func in connections.items():
            self._connections[key] = self._fig.canvas.mpl_connect(key, func)

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
        self._draw()

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
        # self._draw()
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
