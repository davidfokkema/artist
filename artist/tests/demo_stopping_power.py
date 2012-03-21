import numpy as np
from numpy import sqrt
import pylab as plt


def main():
    e_data = np.genfromtxt('estar-plastic-scint.txt', skip_header=8,
                           usecols=(0, 1))
    e_kin_E = e_data[:,0]
    e_mass = .511
    e_beta_gamma = sqrt(e_kin_E / e_mass * (e_kin_E / e_mass + 2))
    e_loss = e_data[:,1]

    mu_data = np.genfromtxt('muonloss_216.dat', usecols=(1, 2))
    mu_p = mu_data[:,0]
    mu_mass = 105.658367
    mu_beta_gamma = mu_p / mu_mass
    mu_loss = mu_data[:,1]

    plt.figure()
    plt.loglog(e_beta_gamma, e_loss, label="e")
    plt.loglog(mu_beta_gamma, mu_loss, label="mu")
    plt.legend()


if __name__ == '__main__':
    main()
