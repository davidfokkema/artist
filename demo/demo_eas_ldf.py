import numpy as np

from artist import Plot


def main():
    gamma = np.genfromtxt('data/showere15-proton.t2001', usecols=(1, 2))
    e = np.genfromtxt('data/showere15-proton.t2205', usecols=(1, 2))
    mu = np.genfromtxt('data/showere15-proton.t2207', usecols=(1, 2))

    graph = Plot(axis='loglog')

    graph.plot(gamma[:, 0], gamma[:, 1], mark=None)
    graph.add_pin(r'$\gamma$')

    graph.plot(e[:, 0], e[:, 1], mark=None)
    graph.add_pin('e')

    graph.plot(mu[:, 0], mu[:, 1], mark=None)
    graph.add_pin(r'$\mu$')

    graph.set_xlabel(r"Core distance [\si{\meter}]")
    graph.set_ylabel(r"Particle density [\si{\per\square\meter}]")
    graph.set_logyticks(range(-6, 3, 2))
    graph.save('eas-lateral')


if __name__ == '__main__':
    main()
