
from setuptools import setup, find_packages


setup(
    name='wordle-solver',
    version='0.4.0',
    license='GPL-3.0',
    author="Kody Puebla",
    author_email='pueblakody@gmail.com',
    packages=find_packages('data'),
    package_dir={'': 'data'},
    include_package_data=True,
    url='https://github.com/pueblak/wordle-solver',
    keywords='example project',
    install_requires=[
          'tqdm', 'selenium'
      ],
    description='A wordle solver that can generate near-optimal decision trees and automatically play on multiple different websites including Quordle and Wordzy'
)

