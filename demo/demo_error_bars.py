import numpy as np

from artist import Plot


def main():
    plot = Plot()

    size = 20
    x = np.linspace(1, 20, size)
    y = np.linspace(10, 50, size)
    y_random = y + np.random.uniform(-3, 1, size)

    err_l = np.random.uniform(0, 2, size)
    err_h = np.random.uniform(1, 5, size)
    err_x = [0.4] * size

    plot.plot(x, y, mark=None)
    plot.scatter(x, y_random, xerr=err_x, yerr=zip(err_l, err_h))

    plot.set_xlabel('Value with symmetric error')
    plot.set_ylabel('Other value with asymmetric errors')
    plot.save('error_bars')


if __name__ == '__main__':
    main()
