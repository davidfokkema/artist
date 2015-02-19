from artist import Plot


def main():
    """Event display for an event of station 503

    Date        Time      Timestamp   Nanoseconds
    2012-03-29  10:51:36  1333018296  870008589

    Number of MIPs
    35.046  51.932  35.780  78.873

    Arrival time
    15      17.5    20      27.5

    """
    scale = 5.
    plot = Plot()
    plot.scatter([0], [0])
    plot.add_pin_at_xy(0, 0, 'Station 503', use_arrow=False, location='below')
    plot.scatter_table([-6.34, -2.23, -3.6, 3.46],
                       [6.34, 2.23, -3.6, 3.46],
                       [15, 17.5, 20, 27.5],
                       [35 / scale, 52 / scale, 36 / scale, 79 / scale])

    plot.set_colorbar('$\Delta$t [ns]')
    plot.set_axis_equal()
    plot.set_xlabel('x [m]')
    plot.set_ylabel('y [m]')

    plot.save('event_display')


if __name__ == '__main__':
    main()
