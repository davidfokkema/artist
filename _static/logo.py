"""Make artist logo

Run this script, then use ImageMagick to make the favicon version:

    python logo.py
    convert -density 768 -resize 32x32 logo.pdf favicon.png

To make a Finder icon use:

    convert -density 12380 -resize 1024x1024 logo.pdf logo.png

"""

from numpy import arange, sin, pi

from artist import Plot


def make_logo():
    size = '.02\linewidth'
    x = arange(0, 2*pi, .01)
    y = sin(x)
    plot = Plot(width=size, height=size)
    plot.set_ylimits(-1.3, 1.3)
    plot.set_yticks([-1, 0, 1])
    plot.set_ytick_labels(['', '', ''])
    plot.set_xticks([0, pi, 2*pi])
    plot.set_xtick_labels(['', '', ''])
    plot.plot(x, y, mark=None, linestyle='thick')
    plot.set_axis_options("axis line style=thick, major tick length=.04cm")
    plot.save_as_pdf('logo')


if __name__ == "__main__":
    make_logo()
