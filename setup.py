import glob
from distutils.core import setup

setup(
  name = 'stdio',
  packages = ['stdio'],
  version = '0.3',
  description = 'A tcp server to invoke python command line utilities',
  long_description = 'A tcp server to invoke python CLI - compatible with http<br>Go to https://github.com/magicray/main-server for details',
  author = 'Bhupendra Singh',
  author_email = 'bhsingh@gmail.com',
  url = 'https://github.com/magicray/main-server',
  keywords = ['stdio', 'main', 'cli', 'command line', 'tcp', 'server', 'http'],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3.7'
  ],
)
