import numpy as np
from numpy import sqrt
import pylab as plt

from artist import GraphArtist

# For TeX rendering
plt.rcParams['font.serif'] = 'Computer Modern'
plt.rcParams['font.sans-serif'] = 'Computer Modern'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.figsize'] = [4 * x for x in (1, 2. / 3)]
plt.rcParams['figure.subplot.left'] = 0.175
plt.rcParams['figure.subplot.bottom'] = 0.175
plt.rcParams['font.size'] = 10
plt.rcParams['legend.fontsize'] = 'small'
plt.rcParams['text.usetex'] = True


def main():
    e_data = np.genfromtxt('estar-plastic-scint.txt', skip_header=8,
                           usecols=(0, 1))
    e_kin_E = e_data[:, 0]
    e_mass = .511
    e_beta_gamma = sqrt(e_kin_E / e_mass * (e_kin_E / e_mass + 2))
    e_loss = e_data[:, 1]

    mu_data = np.genfromtxt('muonloss_216.dat', usecols=(1, 2))
    mu_p = mu_data[:, 0]
    mu_mass = 105.658367
    mu_beta_gamma = mu_p / mu_mass
    mu_loss = mu_data[:, 1]

    plt.figure()
    plt.loglog(e_beta_gamma, e_loss, label="e")
    plt.loglog(mu_beta_gamma, mu_loss, label=r"$\mu$")
    plt.xlabel(r'$\beta\gamma$')
    plt.ylabel('Stopping Power [MeV cm$^2$ g$^{-1}$]')
    plt.legend()
    plt.savefig('demo_plot-mpl.pdf')

    plot = GraphArtist(axis='loglog', width=r'.5\linewidth')
    plot.plot(e_beta_gamma, e_loss, mark=None)
    plot.plot(mu_beta_gamma, mu_loss, mark=None)
    plot.set_xlabel(r'$\beta\gamma$')
    plot.set_ylabel(r'Stopping Power $\left[\si{\mega\electronvolt'
                                              r'\centi\meter\squared'
                                              r'\per\gram}\right]$')
    plot.add_pin(e_beta_gamma, e_loss, 'e', location='below right',
                 relative_position=.8)
    plot.add_pin(mu_beta_gamma, mu_loss, r'$\mu$', 'above left')
    plot.set_xlimits(1e-2, 1e8)
    plot.set_ylimits(min=1)
    plot.set_logxticks(range(-2, 9, 2))

    plot.save('demo_plot')


if __name__ == '__main__':
    main()
