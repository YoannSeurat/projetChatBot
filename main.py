import os 
from math import log
 
def list_of_files(directory, extension):
    files_names = [] 
    for filename in os.listdir(directory): 
        if filename.endswith(extension): 
            files_names.append(filename) 
    return files_names

def cleanSpeeches():
    speeches = list_of_files("speeches", ".txt")
    for speech in speeches:
        with open("speeches\\" + speech, "r", encoding="utf-8") as file:
            lines = file.readlines()
        finalLines = ""
        for s in lines:
            i = 0
            while i < len(s):
                if s[i] in [".", ",", "!", "?", ":", ";", "`"] or (i == 0 and s[i] in ["-", " "]):
                    s = s[:i] + s[i+1:]
                elif s[i] in ["-", "\n", "'"]:
                    s = s[:i] + " " + s[i+1:]
                elif i != len(s)-1 and s[i] == " " and s[i-1] == " ":
                    s = s[:i-1] + s[i:]
                else:
                    if 65 <= ord(s[i]) <= 90:
                        s = s[:i] + chr(ord(s[i]) + (97-65)) + s[i+1:]
                    i += 1
            finalLines += s
        with open("cleaned\\"+speech, "w", encoding="utf-8") as file:
            file.write(''.join(finalLines))
    return 'cleaned'

def create_dictTFScore(string):
    words = string.split()
    frequency = {}
    for word in words:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency

def create_dictIDFScore(directory):
    IDFscores = {}
    allFiles = list_of_files(directory, ".txt")
    allWords = {}
    for filename in allFiles:
        with open(directory+filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
        freq = createDict_TFScore(''.join(lines))
        for word in freq:
            if word in allWords:
                allWords[word] += 1
            else:
                allWords[word] = 1
    for word in allWords:
        IDFscores[word] = round(log(len(allFiles)/allWords[word]), 2)
    return IDFscores

def create_matriceTFIDF(directory):
    