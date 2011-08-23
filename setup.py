try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
  'description': 'Albatross', 
  'author': 'Shal Dengeki', 
  'url': 'http://github.com/shaldengeki/albatross', 
  'download_url': 'http://github.com/shaldengeki/albatross/tarball/master', 
  'author_email': 'shaldengeki@gmail.com', 
  'version': '0.1', 
  'install_requires': ['nose'], 
  'packages': ['albatross'], 
  'scripts': [],
  'name': 'albatross'
}

setup(**config)