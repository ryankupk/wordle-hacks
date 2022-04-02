from os.path import exists
from requests import request

# dictionary of letters that are correct and their known positions
correct = {}
# dictionary of letters and positions that they are known to not be in
inWord = {}
# list of letters that are not in the word
notInWord = []

end = "XXX"

def getPatternCommandline():
    print("Enter xxx to exit")
    # uppercase guess to standardize letters
    guess = input("Enter guess: ").upper()
    if guess != end:
        pattern = input("Enter results\n_ for not in word, lowercase for in word but wrong spot, uppercase for in word and correct spot\n: ")
        setPatterns(guess, pattern)
    return guess


def setPatterns(guess, pattern):
    for i in range(len(guess)):
        # check that the letter at position[i] is not in word
        # duplicate letters cannot be added to the list of letters not in the word if they were otherwise decided to be in the word and/or in the correct place
        if pattern[i] == "_" and guess[i].lower() not in correct.keys() and guess[i].lower() not in inWord.keys():
            notInWord.append(guess[i].lower())
        # check if the letter is in the word and correct place
        elif guess[i] == pattern[i]:
            correct[guess[i].lower()] = i
        # check if the letter is in the word but not in the correct place
        elif guess[i] == pattern[i].upper():
            # if the key for the letter exists, add the position to the list of not possible positions for that letter
            if guess[i].lower() in inWord.keys():
                inWord[guess[i].lower()] += [i]
            else:
                # if the key for the letter does not exist, add it to the dictionary
                inWord[guess[i].lower()] = [i]
        


if __name__ == "__main__":
    allWords = []
    WORD_PATH = "./word list.txt"
    # if word list file exists, use it to populate allWords list
    if exists(WORD_PATH):
        with open(WORD_PATH, "r") as f:
            allWords = f.readlines()
    # else get word list from github and write to disk if desired
    else:
        allWords = request("GET", "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words").text
        makeFile = input("Write word list to disk? (y or n): ")
        if makeFile.upper() == "Y":
            with open(WORD_PATH, "w") as f:
                f.write(allWords)
        
        allWords = allWords.split("\n")
    
    # when the solution is entered and all letters are in the correct place, exit
    while len(correct) < 5:
        guess = getPatternCommandline()
        if guess == end or len(correct) == 5: break
        possibleWords = []
        for word in allWords:
            # flag to skip the word if it doesn't meet criteria that indicate that it could be a possible solution
            skipWord = False
            
            # iterate across known letters and their positions
            for letter, position in correct.items():
                # skip word if a known letter is not in the right spot
                if word[position] != letter:
                    skipWord = True
                    break
            if skipWord: continue
            
            # iterate across letters that are known, and the positions that they're *not* in
            for letter, positions in inWord.items():
                # skip letters that have not been identified to be in the word
                if len(positions) > 0:
                    # skip word if (letter not in word) or ((letter in word) and (letter in known incorrect position))
                    if (letter not in word) or (word.find(letter) in positions):
                        skipWord = True
                        break
            if skipWord: continue

            # if any letters that are known to not be in the word are in the current word, skip it
            for letter in notInWord:
                if letter in word:
                    skipWord = True
                    break
            if skipWord: continue

            # add current word to list of possible words if it passes all above checks
            possibleWords.append(word)

        print("\n")
        print(possibleWords)
        print("\n\n")
        # reduce the search space to only those words that were determined to be possible solutions
        allWords = possibleWords

    print("congratulation.")