from os.path import exists
from requests import request
from json import loads, dumps

# dictionary of letters that are correct and their known positions
correct = {}
# dictionary of letters and positions that they are known to not be in
inWord = {}
# list of letters that are not in the word
notInWord = set()

# list of all possible words
allWords = []
# dictionary of words and their frequency in English
wordFrequency = {}

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
        if pattern[i] == "_" and guess[i].lower() not in correct.keys() and (guess[i].lower() not in inWord.keys() and guess[i] not in guess[i+1:]):
            notInWord.add(guess[i].lower())

        # check if the letter is in the word and correct place
        elif guess[i] == pattern[i]:
            correct[guess[i].lower()] = i

        # check if the letter is in the word but not in the correct place
        elif guess[i] == pattern[i].upper():
            # if the key for the letter exists, add the position to the list of not possible positions for that letter
            if guess[i].lower() in inWord.keys(): inWord[guess[i].lower()] += [i]
                # if the key for the letter does not exist, add it to the dictionary
            else: inWord[guess[i].lower()] = [i]
        
        
def sortPossibleWords(possibleWords):
    # list of words to return
    retList = []
    # start with one arbitrary word in the list
    retList.append(possibleWords[0])

    for posWord in possibleWords[1:]:
        # flag to avoid adding duplicate words to retList
        flag = True
        for j, retWord in enumerate(retList):
            # if the frequency of the current possible word is less than or equal to the frequency of the current word in the list to be returned
            # and the current possible word is not already in the list
            if int(wordFrequency[posWord]) <= int(wordFrequency[retWord]) and posWord not in retList:
                retList.insert(j-1 if j > 0 else j, posWord)
                flag = False
                break
        # insert word into retList only if it's not already in the list
        if flag is True:
            retList.insert(len(retList), posWord)

    return retList




if __name__ == "__main__":

    WORD_PATH = "./word list.txt"
    FREQUENCY_PATH = "./unigram_freq.json"
    # if word list file exists, use it to populate allWords list
    if exists(WORD_PATH):
        with open(WORD_PATH, "r") as f:
            allWords = f.readlines()
    # else get word list from github and write to disk if desired
    else:
        allWords = request("GET", r"https://raw.githubusercontent.com/ryankupk/wordle-hacks/main/word%20list.txt").text
        makeFile = input("Write word list to disk? (y or n): ")
        if makeFile.upper() == "Y":
            with open(WORD_PATH, "w") as f:
                f.write(allWords)
        
        allWords = allWords.split("\n")
        
    # clean newline from word list
    for i in range(len(allWords)):
        word = allWords[i]
        allWords.insert(0, word.strip())
        allWords.remove(word)

    # if word frequency file exists, use it to populate wordFrequency dictionary
    if exists(FREQUENCY_PATH):
        with open(FREQUENCY_PATH, "r") as f:
            wordFrequency = loads(f.read())
    # else get word frequency from github and write to disk if desired
    else:
        wordFrequency = loads(request("GET", "https://raw.githubusercontent.com/ryankupk/wordle-hacks/main/unigram_freq.json").text)
        makeFile = input("Write word frequency to disk? (y or n): ")
        if makeFile.upper() == "Y":
            with open(FREQUENCY_PATH, "w") as f:
                f.write(dumps(wordFrequency))
    
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

        possibleWords = sortPossibleWords(possibleWords)

        print("\n" * 1000)
        print("Possible solutions:")
        for word in possibleWords[:-1]:
            print(word, end=", ")
        print(possibleWords[-1])
        print() 
        print("least likely <----> most likely\n")
        # reduce the search space to only those words that were determined to be possible solutions
        allWords = possibleWords

    print("congratulation.")