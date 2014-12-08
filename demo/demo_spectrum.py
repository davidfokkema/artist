import numpy as np

from artist import Plot


def main():
    leap = np.genfromtxt('data/leap-prot.dat', delimiter=',',
                         usecols=(0, 1), names=['E', 'F'])
    leap['E'] *= 1e6
    leap['F'] *= 1e3 * 2

    proton = read_data('data/proton', 1, 0)
    akeno_new_lo = read_data('data/akeno-new-lo', 0, 1)
    flys_eye = read_data('data/fe-new', 0, 1)
    yakutsk = read_data('data/yakustk', 1, 0)
    haverah = read_data('data/haverah', 1, 0)

    graph = Plot(axis='loglog', width=r'.5\linewidth', height=r'.65\linewidth')

    graph.plot(leap['E'], leap['F'], mark=None)
    graph.add_pin('LEAP', 'above right', use_arrow=True,
                  relative_position=.5)
    graph.plot(proton['E'], proton['F'], mark=None)
    graph.add_pin('PROTON', 'above right', use_arrow=True,
                  relative_position=.5)
    graph.plot(akeno_new_lo['E'], akeno_new_lo['F'], mark=None)
    graph.add_pin('AGASA', 'above right', use_arrow=True,
                  relative_position=.5)

    graph.plot(yakutsk['E'], yakutsk['F'], mark=None)
    graph.add_pin('Yakutsk', 'below left', use_arrow=True,
                  relative_position=.55)
    graph.plot(haverah['E'], haverah['F'], mark=None)
    graph.add_pin('Haverah Park', 'below left', use_arrow=True,
                  relative_position=.85)
    graph.plot(flys_eye['E'], flys_eye['F'], mark=None)
    graph.add_pin("Fly's Eye", 'below left', use_arrow=True,
                  relative_position=1.0)

    graph.set_xlabel(r"Energy [\si{\electronvolt}]")
    graph.set_ylabel(r"Flux [\si{\per\square\meter\per\steradian"
                     "\per\second\per\giga\electronvolt}]")

    x = np.logspace(11, 17)
    graph.plot(x, 1.5e29 * x ** -2.75, mark=None, linestyle='dashed')

    graph.set_logxticks(range(6, 22, 3))
    graph.save('spectrum')


def read_data(path, energy_col, flux_col):
    data = np.genfromtxt(path, usecols=(energy_col, flux_col),
                         names=['E', 'F'])
    data.sort()
    data['F'] /= (data['E'] / 1e9) ** 2.75
    return data


if __name__ == '__main__':
    main()
