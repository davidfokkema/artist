from setuptools import setup, find_packages

setup(name = "artist",
      version = "0.18.2",
      packages = find_packages(),
      url = "http://github.com/davidfokkema/artist/",
      bugtrack_url='http://github.com/davidfokkema/artist/issues',
      license='GPLv3',
      author = "David Fokkema, Arne de Laat",
      author_email = "davidfokkema@icloud.com, arne@delaat.net",
      description = "A plotting library for Python with LaTeX output",
      long_description=open('README.rst').read(),
      keywords=['plots', 'plotting', 'data visualization'],
      classifiers=['Intended Audience :: Science/Research',
                   'Intended Audience :: Education',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Education',
                   'Topic :: Text Processing :: Markup :: LaTeX',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
      install_requires = ['jinja2', 'numpy', 'Pillow'],
      package_data={'artist': ['templates/*.tex']},
)
