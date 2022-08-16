# wordle-hacks

Usage: `python ./wordle.py`

On running the program, "Enter xxx to exit" and "Enter guess: " are printed to the commandline. Either enter `xxx` and press enter to exit (or press control+c) or enter what was guessed in wordle. After, the pattern needs to be entered to determine which letters can and can't go in each spot - 

"Enter results

_ for not in word, lowercase for in word but wrong spot, uppercase for in word and correct spot

: " is printed. An underscore indicates that the corresponding letter was not in the word at all. A lower case letter indicates that the letter was in the word but not in the right spot. An upper case letter indicates that the letter is in the word and in the correct spot. ex:

wordle guess: crane

![Screenshot_20220401-234238~2](https://user-images.githubusercontent.com/34145544/161368523-06d3bc3f-232e-44f4-835f-15fe1d5fb031.png)
text entered after "Enter guess: ": crane

text entered after the next prompt would be __\_N\_

all possible solutions are printed to the console and another prompt for a guess is given in order from least frequently used (top left) to most frequently (bottom right)

subsequent wordle guess: pious

![Screenshot_20220401-234536~2](https://user-images.githubusercontent.com/34145544/161368627-c788e545-3a8c-4e39-89a0-d4c8b4e491b5.png)

text entered after "Enter guess: ": pious

text entered after the next prompt would be P_ou_

etc.

Note: the sorting used is a proxy for likelihood that a possible solution given is the actual solution. Most/all wordle solutions are words that are used at least relatively often (like crane), whereas other allowed guesses may be extremely uncommon (like yodhs or poopy).


Special thanks to [@tabatkins](https://github.com/tabatkins) for uploading the [wordle word list](https://github.com/tabatkins/wordle-list) and [rtatman](https://www.kaggle.com/rtatman) on Kaggle for the [list of words and their frequencies](https://www.kaggle.com/datasets/rtatman/english-word-frequency). 
