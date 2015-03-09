from artist import Plot, MultiPlot


def main():
    """Event display for an event of station 503

    Date        Time      Timestamp   Nanoseconds
    2012-03-29  10:51:36  1333018296  870008589

    Number of MIPs
    35.0  51.9  35.8  78.9

    Arrival time
    15.0  17.5  20.0  27.5

    """
    # Detector positions in ENU relative to the station GPS
    x = [-6.34, -2.23, -3.6, 3.46]
    y = [6.34, 2.23, -3.6, 3.46]

    # Scale mips to fit the graph
    n = [35.0, 51.9, 35.8, 78.9]

    # Make times relative to first detection
    t = [15., 17.5, 20., 27.5]
    dt = [ti - min(t) for ti in t]

    plot = Plot()
    plot.scatter([0], [0], mark='triangle')
    plot.add_pin_at_xy(0, 0, 'Station 503', use_arrow=False, location='below')
    plot.scatter_table(x, y, dt, n)

    plot.set_scalebar(location="lower right")
    plot.set_colorbar('$\Delta$t [ns]')
    plot.set_axis_equal()
    plot.set_mlimits(max=16.)
    plot.set_slimits(min=10., max=100.)

    plot.set_xlabel('x [m]')
    plot.set_ylabel('y [m]')

    plot.save('event_display')


    # Add event by Station 508
    # Detector positions in ENU relative to the station GPS
    x508 = [6.12, 0.00, -3.54, 3.54]
    y508 = [-6.12, -13.23, -3.54, 3.54]

    # Event GPS timestamp: 1371498167.016412100
    # MIPS
    n508 = [5.6, 16.7, 36.6, 9.0]
    # Arrival Times
    t508 = [15., 22.5, 22.5, 30.]
    dt508 = [ti - min(t508) for ti in t508]

    plot = MultiPlot(1, 2, width=r'.33\linewidth')
    plot.set_xlimits_for_all(min=-10, max=15)
    plot.set_ylimits_for_all(min=-15, max=10)
    plot.set_mlimits_for_all(min=0., max=16.)
    plot.set_colorbar('$\Delta$t [ns]', False)
    plot.set_colormap('blackwhite')
    plot.set_scalebar_for_all(location="upper right")

    p = plot.get_subplot_at(0, 0)
    p.scatter([0], [0], mark='triangle')
    p.add_pin_at_xy(0, 0, 'Station 503', use_arrow=False, location='below')
    p.scatter_table(x, y, dt, n)
    p.set_axis_equal()

    p = plot.get_subplot_at(0, 1)
    p.scatter([0], [0], mark='triangle')
    p.add_pin_at_xy(0, 0, 'Station 508', use_arrow=False, location='below')
    p.scatter_table(x508, y508, dt508, n508)
    p.set_axis_equal()

    plot.show_yticklabels_for_all([(0, 0)])
    plot.show_xticklabels_for_all([(0, 0), (0, 1)])

    plot.set_xlabel('x [m]')
    plot.set_ylabel('y [m]')

    plot.save('multi_event_display')


if __name__ == '__main__':
    main()
