import numpy as np
from numpy import sqrt
import pylab as plt

import jinja2


class Artist:
    def __init__(self, axis='', width=r'.67\linewidth'):
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
                                                        'templates'),
                                         finalize=self._convert_none)
        self.template = environment.get_template('artist_plot.tex')

        self.plot_series_list = []
        self.pin_list = []
        self.axis = axis + 'axis'
        self.width = width
        self.xlabel = None
        self.ylabel = None
        self.limits = {'xmin': None, 'xmax': None,
                       'ymin': None, 'ymax': None}
        self.ticks = {'x': [], 'y': []}

    def plot(self, x, y, mark='o', linestyle='solid'):
        options = self._parse_plot_options(mark, linestyle)
        self.plot_series_list.append({'options': options,
                                      'data': zip(x, y)})

    def add_pin(self, x, y, text, location='above right',
                relative_position=.9):
        x, y = self._calc_position_for_pin(x, y, relative_position)
        self.pin_list.append({'x': x, 'y': y, 'text': text,
                              'location': location})

    def render(self):
        response = self.template.render(axis=self.axis,
                                        width=self.width,
                                        xlabel=self.xlabel,
                                        ylabel=self.ylabel,
                                        limits=self.limits,
                                        ticks=self.ticks,
                                        series_list=self.plot_series_list,
                                        pin_list = self.pin_list)
        return response

    def set_xlabel(self, text):
        self.xlabel = text

    def set_ylabel(self, text):
        self.ylabel = text

    def set_xlimits(self, min=None, max=None):
        self.limits['xmin'] = min
        self.limits['xmax'] = max

    def set_ylimits(self, min=None, max=None):
        self.limits['ymin'] = min
        self.limits['ymax'] = max

    def set_xticks(self, ticks):
        self.ticks['x'] = ticks

    def set_logxticks(self, logticks):
        self.ticks['x'] = ['1e%d' % u for u in logticks]

    def set_yticks(self, ticks):
        self.ticks['y'] = ticks

    def set_logyticks(self, logticks):
        self.ticks['y'] = ['1e%d' % u for u in logticks]

    def _parse_plot_options(self, mark, linestyle):
        options = []
        if mark is not None:
            options.append('mark=%s' % mark)
        else:
            options.append('no markers')

        if linestyle is not None:
            options.append(linestyle)
        else:
            options.append('only marks')

        options_string = ','.join(options)
        return options_string

    def _calc_position_for_pin(self, x, y, relative_position):
        try:
            N_x = len(x)
            N_y = len(y)
        except TypeError:
            return x, y
        else:
            assert N_x == N_y, \
                'If x and y are iterables, they must be the same length'
            index = round(N_x * relative_position)
            return x[index], y[index]

    def _convert_none(self, variable):
        if variable is not None:
            return variable
        else:
            return ''


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

    #plt.figure()
    #plt.loglog(e_beta_gamma, e_loss, label="e")
    #plt.loglog(mu_beta_gamma, mu_loss, label="mu")
    #plt.legend()
    #plt.savefig('demo_plot-mpl.pdf')

    plot = Artist(axis='loglog', width=r'.5\linewidth')
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

    with open('demo_plot.tex', 'w') as f:
        f.write(plot.render())


if __name__ == '__main__':
    main()
