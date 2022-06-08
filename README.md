# wordle-solver
A python program that can solve Classic Wordle and many of its variants.

# usage
wordle_solver.py [-h] [-n N] [-hard | -master | -liar] [-auto WEBSITE | -sim MAX_SIMS] [-continue LIMIT | -endless | -challenge] [-best] [-start WORD [WORD ...]]

Solve a Wordle game on one board or multiple by calculating the best guesses at every step.

optional arguments:
  -h, --help            show this help message and exit
  -n N                  number of simultaneous games (default: 1)
  -hard                 use if playing on hard mode (default: False)
  -master               only set this flag if the game does not tell you which colors belong to which letters (default: False)
  -liar                 use if playing Fibble where one letter in each response is always a lie (default: False)
  -auto WEBSITE         set this flag to automate play on the given website (requires chromedriver) -- NOTE: websites with a fixed number of boards will override the N argument for number of boards
  -sim MAX_SIMS         set this flag to simulate MAX_SIMS unique games and give resulting stats
  -continue LIMIT       set this flag to continue playing on multiple boards up to the given number (max 1024) -- setting the limit to "-1" will test all possible starting words to find the best one(s) (be aware that this process may be very slow
  -endless              use to play the same game over and over
  -challenge            play the daily wordle, dordle, quordle, and octordle in order, using the answers from each puzzle as the starting words for the next (inspired by YouTube channel Scott Stro-solves)
  -best                 set this flag to generate a minimal guess tree (be aware that this process may be very slow)
  -start WORD [WORD ...]
                        set this flag if there are certain words you want to start with regardless of the response
