import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='wiiuse',
    version='0.13',
    author='Tim Swast',
    author_email='tswast@gmail.com',

    description='Python wrapper for the wiiuse interface to the Wiimote',
    long_description=read('README'),
    
    license = "BSD",
    keywords = "wii",
    url='http://code.google.com/p/pywiiuse/',
    packages=['wiiuse'],
)

