from setuptools import setup, find_packages
import SLRIC

setup(
    name='slric',
    version=SLRIC.__version__,
    packages=find_packages(),
    url='https://github.com/SergSHV/slric',
    license='BSD 3-clause "New" or "Revised License"',
    author='Fuad Aleskerov, Natalia Meshcheryahkova, Sergey Shvydun(*)',
    author_email='shvydun@hse.ru',
    description='SRIC and LRIC indices calculation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
                       'numpy', 'cvxopt', 'networkx>=2.3']
)
