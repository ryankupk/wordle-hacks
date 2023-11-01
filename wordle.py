from os.path import exists
from requests import request
from json import loads, dumps
from os import system, name

# dictionary of letters that are correct and their known positions
correct = {}
# dictionary of letters and positions that they are known to not be in
in_word = {}
# list of letters that are not in the word
not_in_word = set()

# list of all possible words
all_words = []
# dictionary of words and their frequency in English
word_frequency = {}

END = r"\0"

def cls():
    system('cls' if name == 'nt' else 'clear')

def get_pattern_commandline():
    print(f"Enter {END} to exit")
    # uppercase guess to standardize letters
    guess = input("Enter guess: ").upper()
    if guess != END:
        pattern = input("Enter results\n_ for not in word, lowercase for in word but wrong spot, uppercase for in word and correct spot\n: ")
        set_patterns(guess, pattern)
    return guess


def set_patterns(guess, pattern):
    for i, _ in enumerate(guess):
        # check that the letter at position[i] is not in word
        # duplicate letters cannot be added to the list of letters not in the word if they were otherwise decided to be in the word and/or in the correct place
        if  pattern[i] == "_" and guess[i].lower() not in correct.keys() \
            and (guess[i].lower() not in in_word.keys() \
            and guess[i] not in guess[i+1:]):
                not_in_word.add(guess[i].lower())

        # check if the letter is in the word and correct place
        elif guess[i] == pattern[i]:
            correct[guess[i].lower()] = i

        # check if the letter is in the word but not in the correct place
        elif guess[i] == pattern[i].upper():
            # if the key for the letter exists, add the position to the list of not possible positions for that letter
            if guess[i].lower() in in_word.keys(): in_word[guess[i].lower()] += [i]
                # if the key for the letter does not exist, add it to the dictionary
            else: in_word[guess[i].lower()] = [i]
        
        
def sort_possible_words(possible_words):
    # list of words to return
    return_list = []
    # start with one arbitrary word in the list
    return_list.append(possible_words[0])

    for possible_word in possible_words[1:]:
        # flag to avoid adding duplicate words to return_list
        not_inserted_flag = True
        for j, return_word in enumerate(return_list):
            # if the frequency of the current possible word is less than or equal to the frequency of the current word in the list to be returned
            # and the current possible word is not already in the list
            if int(word_frequency[possible_word]) <= int(word_frequency[return_word]) and possible_word not in return_list:
                return_list.insert(j-1 if j > 0 else j, possible_word)
                not_inserted_flag = False
                break
        # insert word into return_list only if it's not already in the list
        if not_inserted_flag is True:
            return_list.insert(len(return_list), possible_word)

    return return_list




if __name__ == "__main__":

    WORD_PATH = "./word list.txt"
    FREQUENCY_PATH = "./unigram_freq.json"
    # if word list file exists, use it to populate all_words list
    if exists(WORD_PATH):
        with open(WORD_PATH, "r") as f:
            all_words = f.read().splitlines()
    # else get word list from github and write to disk if desired
    else:
        all_words = request("GET", r"https://raw.githubusercontent.com/ryankupk/wordle-hacks/main/word%20list.txt").text
        make_file = input("Write word list to disk? (y or n): ")
        if make_file.upper() == "Y":
            with open(WORD_PATH, "w") as f:
                f.write(all_words)
        
        all_words = all_words.split("\n")
        
    # clean newline from word list
    for i in range(len(all_words)):
        word = all_words[i]
        all_words.insert(0, word.strip())
        all_words.remove(word)

    # if word frequency file exists, use it to populate word_frequency dictionary
    if exists(FREQUENCY_PATH):
        with open(FREQUENCY_PATH, "r") as f:
            word_frequency = loads(f.read())
    # else get word frequency from github and write to disk if desired
    else:
        word_frequency = loads(request("GET", r"https://raw.githubusercontent.com/ryankupk/wordle-hacks/main/unigram_freq.json").text)
        make_file = input("Write word frequency to disk? (y or n): ")
        if make_file.upper() == "Y":
            with open(FREQUENCY_PATH, "w") as f:
                f.write(dumps(word_frequency))
    
    # when the solution is entered and all letters are in the correct place, exit
    while len(correct) < 5:
        guess = get_pattern_commandline()
        if guess == END or len(correct) == 5: break
        possible_words = []
        for word in all_words:
            # flag to skip the word if it doesn't meet criteria that indicate that it could be a possible solution
            skip_word_flag = False
            
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
