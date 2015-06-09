import numpy as np

from artist import Plot


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


if __name__ == '__main__':
    main()
