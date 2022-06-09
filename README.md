# Wordle Solver
A python program that can solve the Wordle word-guessing game and many of its variants.

## Setup
Must download and install the following packages from pip:
```bash
pip install tqdm
pip install selenium
pip install chromedriver-autoinstaller
```
Then run the following two lines in a python program:
```python
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
```
Note: The program will still compile and run without selenium or chromedriver, but the "-auto" flag will throw errors if set.

### Other
Must [install chromedriver](https://chromedriver.chromium.org/getting-started) on your device and [add to PATH](https://zwbetz.com/download-chromedriver-binary-and-add-to-your-path-for-automated-functional-testing/) environment variable ([alternative method](https://pypi.org/project/chromedriver-autoinstaller/))

## Usage
```
wordle_solver.py [-h] [-n N] [-hard | -master | -liar] [-auto WEBSITE | -sim MAX_SIMS] [-quiet]
                 [-nyt] [-continue LIMIT | -endless | -challenge] [-best] [-start WORD [WORD ...]]

Solve a Wordle game on one board or multiple by calculating the best guesses at every step.

Calling this program with no arguments will start a solver for 

optional arguments:
  -h, --help            show this help message and exit
  -n N                  number of simultaneous games (default: 1)
  -hard                 use if playing on hard mode (default: False)
  -master               only set this flag if the game does not tell you which colors belong to
                        which letters (default: False)
  -liar                 use if playing Fibble where one letter in each response is always a lie
                        (default: False)
  -auto WEBSITE         set this flag to automate play on the given website (requires chromedriver)
                        -- NOTE: websites with a fixed number of boards will override the N
                        argument for number of boards -- valid websites are: 'wordle', 'wordzy',
                        'dordle', 'quordle', 'octordle', 'sedecordle', 'duotrigordle', '64ordle',
                        and 'nordle'
  -sim MAX_SIMS         set this flag to simulate MAX_SIMS unique games and give resulting stats
  -quiet                hide all unnecessary console output
  -nyt                  only consider answers that are in the New York Times official word list
  -continue LIMIT       set this flag to continue playing on multiple boards up to the given number
                        (max 1024) -- setting the limit to "-1" will test all possible starting
                        words to find the best one(s) (be aware that this process may be very slow
  -endless              use to play the same game over and over
  -challenge            play the daily Wordle, Dordle, Quordle, and Octordle in order, using the
                        answers from each puzzle as the starting words for the next (inspired by
                        YouTube channel Scott Stro-solves)
  -best                 set this flag to generate a minimal guess tree (be aware that this process
                        may be very slow)
  -start WORD [WORD ...]
                        set this flag if there are certain words you want to start with regardless
                        of the response
```