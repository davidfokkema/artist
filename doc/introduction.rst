Introduction
============

Artist enables you to visualize the results of your data analysis.  The
quality of your plots should reflect the quality of your analysis.  With
most software, this is hardly possible and the term 'publication quality'
takes on an entirely new meaning.  As a result, many papers and theses
suffer from inconsistent and generally poor-quality plots.

Fortunately, some solutions are available.  For LaTeX users, one can use
PGF/TikZ for generating figures and plots.  This ensures a very consistent
display throughout your document.  PGFPLOTS builds on that to provide a
user-friendly interface for many kinds of plots and to allow extensive
customization.

For many users, however, it is more convenient to use a programmatic
interface from your favorite programming language.  For Python, such an
interface is available in Artist.

Artist can be used in place of other plotting libraries, but the output is
a LaTeX file requiring PGF/TikZ and PGFPLOTS.  Previewing the output is
possible by means of a simple method which renders the plot as a PDF.

The style of the plots is based on the work of William S. Cleveland.


Usage
-----

Example script::

    import artist
    import numpy as np

    plot = artist.Plot()
    x = np.linspace(0, 10)
    y = x ** 2
    plot.plot(x, y)
    plot.set_xlabel("Number")
    plot.set_ylabel("Square")
    plot.save('somefile')           # will save a LaTeX file
    plot.save_as_pdf('otherfile')   # will directly compile to PDF

The LaTeX file can be compiled directly (e.g. using ``pdflatex``) or can be included in your main document like so::

    \begin{figure}
    \centering
    \input{somefile}
    \caption{A sample figure.}
    \end{figure}

This has the advantage that the image will change size if you change the margins of your document and will use the same fonts as your main document. You do need to include all packages used by Artist, as well as the ``standalone`` package. You can see which packages to use by inspecting the preamble of the generated LaTeX file. Including the ``standalone`` package, your preamble should be something like this::

    \usepackage{standalone}

    \usepackage{tikz}
    \usetikzlibrary{arrows,external}
    \usepackage{pgfplots}
    \pgfplotsset{compat=1.10}
    \usepgfplotslibrary{polar}
    \usepackage[detect-family]{siunitx}
    \usepackage[eulergreek]{sansmath}
    \sisetup{text-sf=\sansmath}
    \usepackage{relsize}
