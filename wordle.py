from os.path import exists
from requests import request
from json import loads, dumps
from os import system, name

# dictionary of letters that are correct and their known positions
correct: dict = {}
# dictionary of letters and positions that they are known to not be in
in_word: dict = {}
# list of letters that are not in the word
not_in_word = set()

# list of all possible words
all_words: list[str] = []
# dictionary of words and their frequency in English
word_frequency: dict = {}

END: str = r"\0"

def cls():
    system('cls' if name == 'nt' else 'clear')

def get_pattern_commandline() -> str:
    print(f"Enter {END} to exit")
    # uppercase guess to standardize letters
    guess: str = input("Enter guess: ").upper()
    if guess != END:
        pattern: str = input("Enter results\n_ for not in word, lowercase for in word but wrong spot, uppercase for in word and correct spot\n: ")
        set_patterns(guess, pattern)
    return guess


def set_patterns(guess: str, pattern: str) -> None:
    for idx, _ in enumerate(guess):
        # check that the letter at position[idx] is not in word
        # duplicate letters cannot be added to the list of letters not in the word if they were otherwise decided to be in the word and/or in the correct place
        if  pattern[idx] == "_" and guess[idx].lower() not in correct.keys() \
            and (guess[idx].lower() not in in_word.keys() \
            and guess[idx] not in guess[idx+1:]):
                not_in_word.add(guess[idx].lower())

        # check if the letter is in the word and correct place
        elif guess[idx] == pattern[idx]:
            correct[guess[idx].lower()] = idx 

        # check if the letter is in the word but not in the correct place
        elif guess[idx] == pattern[idx].upper():
            # if the key for the letter exists, add the position to the list of not possible positions for that letter
            if guess[idx].lower() in in_word.keys(): in_word[guess[idx].lower()] += [idx]
                # if the key for the letter does not exist, add it to the dictionary
            else: in_word[guess[idx].lower()] = [idx]
        
        
def sort_possible_words(possible_words: list[str]) -> list[str]:
    # list of words to return
    return_list: list[str] = []
    # start with one arbitrary word in the list
    return_list.append(possible_words[0])

    for possible_word in possible_words[1:]:
        # flag to avoid adding duplicate words to return_list
        not_inserted_flag: bool = True
        
        for idx, return_word in enumerate(return_list):
            # if the frequency of the current possible word is less than or equal to the frequency of the current word in the list to be returned
            # and the current possible word is not already in the list
            if int(word_frequency[possible_word]) <= int(word_frequency[return_word]) and possible_word not in return_list:
                return_list.insert(idx-1 if idx > 0 else idx, possible_word)
                not_inserted_flag = False
                break
        # insert word into return_list only if it's not already in the list
        if not_inserted_flag is True:
            return_list.insert(len(return_list), possible_word)

    return return_list

def main() -> None:
    WORD_PATH: str = "./word list.txt"
    FREQUENCY_PATH: str = "./unigram_freq.json"
    # if word list file exists, use it to populate all_words list
    if exists(WORD_PATH):
        with open(WORD_PATH, "r") as f:
            global all_words 
            all_words = f.read().splitlines()
    # else get word list from github and write to disk if desired
    else:
        global all_words
        all_words = request("GET", r"https://raw.githubusercontent.com/ryankupk/wordle-hacks/main/word%20list.txt").text
        make_file: str = input("Write word list to disk? (y or n): ")
        if make_file.upper() == "Y":
            with open(WORD_PATH, "w") as f:
                f.write(all_words)
        

    # if word frequency file exists, use it to populate word_frequency dictionary
    if exists(FREQUENCY_PATH):
        with open(FREQUENCY_PATH, "r") as f:
            global word_frequency
            word_frequency = loads(f.read())
    # else get word frequency from github and write to disk if desired
    else:
        global word_frequency
        word_frequency = loads(request("GET", r"https://raw.githubusercontent.com/ryankupk/wordle-hacks/main/unigram_freq.json").text)
        make_file: str = input("Write word frequency to disk? (y or n): ")
        if make_file.upper() == "Y":
            with open(FREQUENCY_PATH, "w") as f:
                f.write(dumps(word_frequency))
    
    # when the solution is entered and all letters are in the correct place, exit
    while len(correct) < 5:
        guess: str = get_pattern_commandline()
        if guess == END or len(correct) == 5: break
        possible_words: list[str] = []
        for word in all_words:
            # flag to skip the word if it doesn't meet criteria that indicate that it could be a possible solution
            skip_word_flag: bool = False
            
            # iterate across known letters and their positions
            for letter, position in correct.items():
                # skip word if a known letter is not in the right spot
                if word[position] != letter:
                    skip_word_flag = True
                    break
            if skip_word_flag: continue
            
            # iterate across letters that are known, and the positions that they're *not* in
            for letter, positions in in_word.items():
                # skip word if (letter not in word) or ((letter in word) and (letter in known incorrect position))
                if (letter not in word) or (word.find(letter) in positions):
                    skip_word_flag = True
                    break
            if skip_word_flag: continue

            # if any letters that are known to not be in the word are in the current word, skip it
            for letter in not_in_word:
                if letter in word:
                    skip_word_flag = True
                    break
            if skip_word_flag: continue

            # add current word to list of possible words if it passes all above checks
            possible_words.append(word)

        possible_words = sort_possible_words(possible_words)

        cls()
        print("Possible solutions:")
        for word in possible_words[:-1]:
            print(word, end=", ")
        print(possible_words[-1])
        print() 
        print("least likely <----> most likely\n")
        # reduce the search space to only those words that were determined to be possible solutions
        all_words = possible_words

    print("congratulation.")


if __name__ == "__main__":
    main()