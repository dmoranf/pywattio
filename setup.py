from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
  name = 'pywattio',
  packages = ['pywattio'],
  version = '0.1.0dev',
  license='MIT',
  description = 'Wattio SmartHome API Wrapper',
  long_description = readme(),
  author = 'dmoranf',
  author_email = 'dmoranf@gmail.com',
  url = 'https://github.com/dmoranf/pywattio',
  download_url = 'https://github.com/dmoranf/pywattio/archive/v_01.tar.gz',
  keywords = ['Wattio Smarthome', 'Wattio API'],
  install_requires = [
    'requests'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Topic :: Home Automation',
    "Operating System :: OS Independent",

  ],
)