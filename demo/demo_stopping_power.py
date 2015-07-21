import numpy as np
from numpy import sqrt

from artist import Plot


def main():
    e_data = np.genfromtxt('data/estar-plastic-scint.txt', skip_header=8,
                           usecols=(0, 1))
    e_kin_E = e_data[:, 0]
    e_mass = .511
    e_beta_gamma = sqrt(e_kin_E / e_mass * (e_kin_E / e_mass + 2))
    e_loss = e_data[:, 1]

    mu_data = np.genfromtxt('data/muonloss_216.dat', usecols=(1, 2))
    mu_p = mu_data[:, 0]
    mu_mass = 105.658367
    mu_beta_gamma = mu_p / mu_mass
    mu_loss = mu_data[:, 1]

    # Artist
    plot = Plot(axis='loglog')
    plot.plot(e_beta_gamma, e_loss, mark=None)
    plot.plot(mu_beta_gamma, mu_loss, mark=None)
    plot.set_xlabel(r'$\beta\gamma$')
    plot.set_ylabel(r'Stopping Power $\left[\si{\mega\electronvolt'
                    r'\centi\meter\squared\per\gram}\right]$')

    plot.add_pin_at_xy(e_beta_gamma, e_loss, 'e', location='below right',
                       relative_position=.8)
    plot.add_pin_at_xy(mu_beta_gamma, mu_loss, r'$\mu$', 'above left')

    plot.set_xlimits(1e-2, 1e8)
    plot.set_ylimits(min=1)
    plot.set_logxticks(range(-2, 9, 2))
    plot.save('stopping-power')


if __name__ == '__main__':
    main()
