# Wordle Solver
## A python package designed to solve the popular word-guessing game and many of its variants.

![Python](https://img.shields.io/badge/python-3670A0?style=style-plastic-03650f&logo=python&logoColor=ffdd54) ![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=style-plastic-03650f&logo=selenium&logoColor=white) ![Google Chrome](https://img.shields.io/badge/Google%20Chrome-4285F4?style=style-plastic-03650f&logo=GoogleChrome&logoColor=white) ![Tests](https://github.com/pueblak/wordle-autosolver/actions/workflows/tests.yml/badge.svg)

![Initial Demo](img/overall-demo.gif)

## Setup
You may download and install this package using pip
```bash
pip install wordle-autosolver
```
Google Chrome and ChromeDriver are also required to be installed on your device. There is a python package that will do this for you called [`chromedriver-autoinstaller`](https://pypi.org/project/chromedriver-autoinstaller/).

Otherwise, use [this link](https://chromedriver.chromium.org/getting-started) to go to the chromedriver page and follow the installation instructions.

Alternatively, if you do not wish to use the auto-solve feature, you may download [`wordle-autosolver-lite`](https://pypi.org/project/wordle-autosolver-lite/) for the version without selenium.

![Wordle Demo](img/wordle-demo.gif)

## Usage
Use this module to solve Wordle and other similar puzzles. Default behavior requires the user to interact with the program through the console. This program will use the user's guess and the game's response to filter a list of possible answers. It will then check every possible guess the user could make next, and check the size of the answer list after each possible response. The program will then recommend the guesses which have the smallest worst-case response. The "-auto" flag allows the user to automate the entry of guesses and responses by connecting to websites and interacting with them using chromedriver + selenium. Current supported websites include: [Wordle](www.nytimes.com/games/wordle/index.html), [Dordle](zaratustra.itch.io/dordle), [Quordle](www.quordle.com), [Octordle](octordle.com), [Sedecordle](www.sedecordle.com), [Duotrigordle](duotrigordle.com), [64ordle](64ordle.au), [Nordle](www.nordle.us), [Wordzy](wordzmania.com/Wordzy), and [Fibble](fibble.xyz).
```
python wordle_autosolver [-h] [--num N] [--nyt | --hard | --master | --liar] [--best] [--quiet]
                         [--play | --auto WEBSITE | --sim MAX_SIMS] [--start WORD [WORD ...]]
                         [--continue LIMIT | --endless | --challenge] [--light] [--clean]

optional arguments:
  -h, --help            show this help message and exit
  --num N               number of simultaneous games (default: 1)
  --nyt                 only consider answers that are in the New York Times official word list
  --hard                use if playing on hard mode (default: False)
  --master              only set this flag if the game does not tell you which colors belong to
                        which letters (default: False)
  --liar                use if playing Fibble where one letter in each response is always a lie
                        (default: False) (currently does not support use with "auto" flag)
  --best                set this flag to generate a minimal guess tree (be aware that this process
                        may be very slow) once completed, the program will continue as normal using 
                        this generated tree to recommend guesses
  --quiet               hide all unnecessary console output
  --play                set this flag to play a game of Wordle using the command line
  --auto WEBSITE        set this flag to automate play on the given website (requires chromedriver)
                        -- NOTE: websites with a fixed number of boards will override the N
                        argument for number of boards -- valid websites are: 'wordle', 'wordzy',
                        'dordle', 'quordle', 'octordle', 'sedecordle', 'duotrigordle', '64ordle',
                        'nordle', and 'fibble'
  --sim MAX_SIMS        set this flag to simulate MAX_SIMS unique games and give resulting stats
  --start WORD [WORD ...]
                        set this flag if there are certain words you want to start with regardless
                        of the response
  --continue LIMIT      set this flag to continue playing on multiple boards up to the given number
                        (max 500) -- setting the limit to "-1" will test all possible starting
                        words to find the best one(s) (be aware that this process may be very slow)
  --endless             use to play the same game over and over -- when used with "-auto wordzy",
                        will play Wordzy's Maniac mode where the number of games increment by one
  --challenge           play the daily Wordle, Dordle, Quordle, and Octordle in order, using the
                        answers from each puzzle as the starting words for the next (inspired by
                        YouTube channel Scott Stro-solves)
  --light               set this flag to force all websites to switch to light mode (if available)
                        -- when "auto" is not set, this flag is ignored
  --clean               empty the contents of "data/best_guess.json", "data/responses.json", and
                        each of their variants to relieve some storage space (the program will not
                        execute any other commands when this flag is set)
```

![Quordle Demo](img/quordle-demo.gif)

## Example Console Output
```
$ python wordle_autosolver --auto wordle --num 4 --start lucky words
Loading precalculated data...
Finished loading.

Connecting to the target website...
Connected to 'https://www.quordle.com/#/'

Starting solver. Simulating 4 simultaneous Wordle games.

Suggested starting word is SALON


Solved  0/4  boards: [*****, *****, *****, *****]

  Predetermined guess is LUCKY

  Response was "....." on board 1
  Best guess(es) on board 1: SANER
    1576 possible answers
  Response was "....." on board 2
  Best guess(es) on board 2: SANER
    1576 possible answers
  Response was "..+.." on board 3
  Best guess(es) on board 3: SHORE
    309 possible answers
  Response was ".O..." on board 4
  Best guess(es) on board 4: TERMS, TREMS
    149 possible answers

Solved  0/4  boards: [*****, *****, *****, *U***]

  Predetermined guess is WORDS

  Response was "+...+" on board 1
  Best guess(es) on board 1: POINT, MEANT, PHASE, SHAPE, PRINT, SAINT, SPITE, PAINT, ...
    18 possible answers
  Response was ".O..+" on board 2
  Best guess(es) on board 2: MEDIA, EMAIL, MERIT, FISTS, THINE, MAIZE, MISTY, AMINE, ...
    18 possible answers
  Response was "...O." on board 3

    The answer on board 3 is CHIDE

  Response was "....O" on board 4
  Best guess(es) on board 4: PETIT, BATHE, INEPT, MOTEN, PATEN, PETTI, MEINT
    34 possible answers

Solved  1/4  boards: [*****, *O***, CHIDE, *U**S]

  Guessing CHIDE...

  Response was "....+" on board 1
  Best guess(es) on board 1: SWEEP
    4 possible answers: SWEET, SWEPT, SWEAT, SWEEP
  Response was "....O" on board 2
  Best guess(es) on board 2: AMONG, ALONG, WRONG, SIGNS, GROWN, SONGS, MASON, AGONY, ...
    4 possible answers: GOOSE, MOOSE, NOOSE, POSSE
  Response was "....+" on board 4
  Best guess(es) on board 4: THUMB, TOMBS, AMBIT, TIMBO
    10 possible answers

Solved  1/4  boards: [SWE**, *O*SE, CHIDE, *U**S]

  Guessing AMBIT...

  Response was "....." on board 1

    The answer on board 1 is SWEEP

  Response was ".+..." on board 2

    The answer on board 2 is MOOSE

  Response was "....." on board 4
  Best guess(es) on board 4: GUESS, FUSES
    2 possible answers: GUESS, FUSES

Solved  3/4  boards: [SWEEP, MOOSE, CHIDE, *U**S]

  Guessing SWEEP...

  Response was "+.O.." on board 4

    The answer on board 4 is GUESS


Solve complete.

Entering all remaining answers... (2 total)
  Entered     1/4    SWEEP
  Entering    2/4    MOOSE
  Entered     3/4    CHIDE
  Entering    4/4    GUESS
Saving all newly discovered data...
Save complete.
PRESS ENTER TO EXIT
```

![Fibble Demo](img/fibble-demo.gif)
