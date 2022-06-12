
from setuptools import setup, find_packages


setup(
    name='wordle-autosolver',
    version='0.4.1',
    license='GPL-3.0',
    author="Kody Puebla",
    author_email='pueblakody@gmail.com',
    packages=find_packages('data'),
    package_dir={'': 'data'},
    include_package_data=True,
    url='https://github.com/pueblak/wordle-solver',
    keywords=['wordle', 'solver', 'selenium', 'chromedriver'],
    install_requires=[
        'tqdm', 'selenium'
    ],
    description=(
        'A Wordle solver that can generate near-optimal decision trees and '
        'automatically play on multiple different website including Quordle '
        'and Wordzy'
    ),
    long_description=(
        'Use this module to solve Wordle and other similar puzzles. Default '
        'behavior requires the user to interact with the program through the '
        'console. This program will use the user\'s guess and the game\'s '
        'response to filter a list of possible answers. It will then check '
        'every possible guess the user could make next, and check the size of '
        'the answer list after each possible response. The program will then '
        'recommend the guesses which have the smallest worst-case response. '
        'The "-auto" flag allows the user to automate the entry of guesses '
        'and responses by connecting to websites and interacting with them '
        'using chromedriver + selenium. Current supported websites include: '
        'Wordle(www.nytimes.com/games/wordle/index.html), '
        'Dordle(zaratustra.itch.io/dordle), Quordle(www.quordle.com), '
        'Octordle(octordle.com), Sedecordle(www.sedecordle.com), '
        'Duotrigordle(duotrigordle.com), 64ordle(64ordle.au), '
        'Nordle(www.nordle.us), Wordzy(wordzmania.com/Wordzy), '
        'and Fibble(fibble.xyz)'
    )
)
