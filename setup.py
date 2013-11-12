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
  'version': '3.02', 
  'install_requires': ['pycurl', 'pytz'], 
  'packages': ['albatross'], 
  'scripts': [],
  'name': 'albatross'
}

setup(**config)
