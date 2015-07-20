import numpy as np

from artist import Plot, MultiPlot


def main():
    x = np.arange(10)
    y = (x / 2.) - 3.
    colors = ['black', 'red', 'blue', 'yellow', 'purple']
    plot = Plot()

    for i in range(5):
        plot.plot(x, y - i, mark='', linestyle=colors[i])

    plot.set_axis_options('yticklabel pos=right,\n'
                          'grid=major,\n'
                          'legend entries={$a$,[red]$b$,[green]$c$,$d$,$a^2$},\n'
                          'legend pos=north west')

    plot.set_xlabel('Something important')
    plot.set_ylabel('A related thing')
    plot.save('any_option')

    x = np.linspace(.6 * np.pi, 10 * np.pi, 150)
    y = np.sin(x) / x
    plot = MultiPlot(1, 2, width=r'.4\linewidth', height=r'.25\linewidth')

    subplot = plot.get_subplot_at(0, 0)
    subplot.plot(x, y, mark=None)

    subplot = plot.get_subplot_at(0, 1)
    subplot.plot(x, y, mark=None)

    plot.show_xticklabels_for_all([(0, 0), (0, 1)])
    plot.show_yticklabels(0, 1)
    plot.set_axis_options(0, 1, 'yticklabel pos=right, grid=major')

    plot.set_axis_options_for_all(None, r'enlargelimits=false')

    plot.set_xlabel('Something important')
    plot.set_ylabel('A related thing')
    plot.save('multi_any_option')


if __name__ == '__main__':
    main()
