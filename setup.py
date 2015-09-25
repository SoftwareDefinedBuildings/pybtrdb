from distutils.core import setup
setup(
  name = 'btrdb',
  packages = ['btrdb'],
  version = '0.1',
  install_requires = ['isodate', 'requests'],
  description = 'Python bindings for BTrDB',
  author = 'Michael P Andersen',
  author_email = 'm.andersen@cs.berkeley.edu',
  url = 'https://github.com/SoftwareDefinedBuildings/pybtrdb',
  keywords = ['BTrDB', 'timeseries'],
  classifiers = [],
)
