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
                elif s[i] == "É":
                    s = s[:i] + "é" + s[i+1:]
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

def create_dictIDFScore(directory, filename):
    IDFscore = {}
    with open(directory+filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    freq = create_dictTFScore(''.join(lines))
    for word in freq:
        IDFscore[word] = round(log(freq[word]), 2)
    return IDFscore

def create_matriceTFIDF_and_allWords(directory):
    allFiles = list_of_files(directory, ".txt")
    allWords = []
    for f in allFiles:
        with open(directory+f, "r", encoding="utf-8") as file:
            lines = file.readlines()
        for w in lines[0].split():
            if w not in allWords:
                allWords.append(w)

    matrice = [[0 for j in range(len(allWords))] for i in range(len(allFiles))] #ligne = document, colonne = mot
    for i in range(len(allFiles)):
        with open(directory+allFiles[i], "r", encoding="utf-8") as file:
            lines = file.readlines()
        freq = create_dictTFScore(''.join(lines))
        for j in range(len(allWords)):
            if allWords[j] in freq:
                matrice[i][j] = round(freq[allWords[j]] * create_dictIDFScore(directory, allFiles[i])[allWords[j]], 2)
    
    matriceTransposee = [[matrice[j][i] for j in range(len(matrice))] for i in range(len(matrice[0]))]
    return matriceTransposee, allWords

def display_matriceTIDF(directory):
    m, allWords = create_matriceTFIDF_and_allWords(directory)
    allFiles = list_of_files(directory, ".txt")
    
    file = open("matriceTIDF.csv", "w", encoding="utf-8")
    
    file.write("Mot;" + ";".join(allFiles) + "\n")
    for k in range(len(allWords)):
        file.write(allWords[k] + ";" + ";".join([str(m[k][i]) for i in range(len(m[k]))]) + "\n")
    file.close()
    return 0

def main():
    cleanSpeeches()
    matriceTFIDF, allWords = create_matriceTFIDF_and_allWords("cleaned\\")
    action = int(input("""Que voulez-vous faire ?
(0. Quitter)
1. Afficher les mots les moins importants
2. Afficher les mots au score TF-IDF le plus élevé
3. Indiquer les mots les plus répétés par Chirac
4. Indiquer les noms des présidents qui ont parlé de la « Nation » et celui qui l’a répété le plus de fois
5. Indiquer le premier président à parler du climat et/ou de l’écologie
6. Afficher les mots que tous les présidents ont utilisés (hormis non-importants)
 > """))
    while action != 0:
        match action:
            case 1:
                for i in range(len(allWords)):
                    if matriceTFIDF[i] == [0 for _ in range(8)]:
                        print(allWords[i], end=", ")
                print("\n")
            case 2:
                motsScoreMax = {str(k): [0 for _ in range(8)] for k in range(5)}
                
                
        action = int(input("""Que voulez-vous faire ?
(0. Quitter)
1. Afficher les mots les moins importants
2. Afficher les mots au score TF-IDF le plus élevé
3. Indiquer les mots les plus répétés par Chirac
4. Indiquer les noms des présidents qui ont parlé de la « Nation » et celui qui l’a répété le plus de fois
5. Indiquer le premier président à parler du climat et/ou de l’écologie
6. Afficher les mots que tous les présidents ont utilisés (hormis non-importants)
 > """))

if __name__ == "__main__":
    main()