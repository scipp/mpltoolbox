class DrawLine:

    def __init__(self, ax):
        self._ax = ax
        self._fig = ax.get_figure()
        self.vertices = None
        self.line = ax.plot(self._ax.get_xlim()[0],
                            self._ax.get_ylim()[0],
                            'o',
                            ls='solid')[0]

        self._fig.canvas.mpl_connect('motion_notify_event', move_dot)

    def move_dot(event):
        if None not in (event.xdata, event.ydata):
            lines[0].set_data((np.array([event.xdata]), np.array([event.ydata])))

    # fig.canvas.mpl_connect('motion_notify_event', move_dot)