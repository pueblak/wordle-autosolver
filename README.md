# Wordle Solver
A python program that can solve the Wordle word-guessing game and many of its variants.

## Setup
You may download and install this package using pip:
```bash
pip install wordle-autosolver
```

## Usage
```
python -m wordle-autosolver [-h] [-n N] [-nyt | -hard | -master | -liar] [-best] [-quiet] [-clean]
                            [-auto WEBSITE | -sim MAX_SIMS] [-continue LIMIT | -endless | -challenge]
                            [-start WORD [WORD ...]]

Solve a Wordle game on one board or multiple by calculating the best guesses at every step.

Calling this program with no arguments will start a solver for a single game and request manual
input of the guesses and responses from the user.

optional arguments:
  -h, --help            show this help message and exit
  -n N                  number of simultaneous games (default: 1)
  -nyt                  only consider answers that are in the New York Times official word list
  -hard                 use if playing on hard mode (default: False)
  -master               only set this flag if the game does not tell you which colors belong to
                        which letters (default: False)
  -liar                 use if playing Fibble where one letter in each response is always a lie
                        (default: False) (currently does not support use with "auto" flag)
  -sim MAX_SIMS         set this flag to simulate MAX_SIMS unique games and give resulting stats
  -best                 set this flag to generate a minimal guess tree (be aware that this process
                        may be very slow)
  -quiet                hide all unnecessary console output
  -clean                empty the contents of "data/best_guess.json", "data/responses.json", and
                        each of their variants to relieve some storage space (the program will not
                        execute any other commands when this flag is set)
  -auto WEBSITE         set this flag to automate play on the given website (requires chromedriver)
                        -- NOTE: websites with a fixed number of boards will override the N
                        argument for number of boards -- valid websites are: 'wordle', 'wordzy',
                        'dordle', 'quordle', 'octordle', 'sedecordle', 'duotrigordle', '64ordle',
                        'nordle', and 'fibble'
  -continue LIMIT       set this flag to continue playing on multiple boards up to the given number
                        (max 500) -- setting the limit to "-1" will test all possible starting
                        words to find the best one(s) (be aware that this process may be very slow)
  -endless              use to play the same game over and over
  -challenge            play the daily Wordle, Dordle, Quordle, and Octordle in order, using the
                        answers from each puzzle as the starting words for the next (inspired by
                        YouTube channel Scott Stro-solves)
  -start WORD [WORD ...]
                        set this flag if there are certain words you want to start with regardless
                        of the response
```
