import os 
from math import log10, sqrt
 
def list_of_files(directory, extension):
    # Retourne la liste des fichiers d'un répertoire d'une certaine extension
    return [filename for filename in os.listdir(directory) if filename.endswith(extension)] 

def list_of_presidents(directory):
    # Retourne la liste des présidents
    presidents = []
    files = list_of_files(directory, ".txt")
    for filename in files:
        filename = filename.split("_")[1]
        filename = filename.split(".")[0]
        if 48 <= ord(filename[-1]) <= 57: # enleve le chiffre à la fin du nom s'il y en a un
            filename = filename[:-1]
        presidents.append(filename) # on laisse intentionnelement les doublons pour que l'indice de chaque président corresponde à son numéro dans la matrice TF-IDF
    return presidents

def cleanSpeeches():
    # Nettoie les discours et les enregistre dans un nouveau dossier 'cleaned'
    speeches = list_of_files("speeches", ".txt")
    for speech in speeches:
        with open("speeches\\" + speech, "r", encoding="utf-8") as file:
            lines = file.readlines()
        finalLines = "" # contiendra le discours nettoyé
        for s in lines:
            i = 0
            while i < len(s):
                if s[i] in [".", ",", "!", "?", ":", ";", "`"] or (i == 0 and s[i] in ["-", " "]): # caractères de ponctuation
                    s = s[:i] + s[i+1:]
                elif s[i] in ["-", "\n", "'"]: # caractères spéciaux a remplacer par un espace
                    s = s[:i] + " " + s[i+1:]
                elif i != len(s)-1 and s[i-1:i+1] == "  ": # 2 espaces consécutifs
                    s = s[:i-1] + s[i:]
                else: # s[i] est une lettre
                    if 65 <= ord(s[i]) <= 90: # majuscule
                        s = s[:i] + chr(ord(s[i]) + (97-65)) + s[i+1:]
                    elif s[i] == "É":
                        s = s[:i] + "é" + s[i+1:]
                    i += 1
            finalLines += s
        with open("cleaned\\"+speech, "w", encoding="utf-8") as file:
            file.write(''.join(finalLines))
    return 'cleaned'

def create_dictTFScore(string):
    # Retourne un dictionnaire avec les mots et leur fréquence d'apparition (score TF)
    words = string.split()
    frequency = {}
    for word in words:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency

def create_dictIDFScore(string):
    # Retourne un dictionnaire avec les mots et leur score IDF
    freq = create_dictTFScore(string)
    return {word : round(log10(freq[word])+1, 2) for word in freq}

def create_matriceTFIDF_and_allWords(directory):
    # Retourne un tuple contenant: 
    #  - la matrice de scores TF-IDF, où chaque ligne correspond à un mot et chaque colonne va avec un fichier du dossier 'cleaned'
    #  - la liste de tous les mots existants dans tous les fichiers
    allFiles = list_of_files(directory, ".txt")
    allWords = []
    for f in allFiles: #creation de la liste allWords
        with open(directory+f, "r", encoding="utf-8") as file:
            lines = file.readlines()
        for w in lines[0].split():
            if w not in allWords and len(w) > 1: # on considere que les mots d'une lettre sont non-importants
                allWords.append(w)

    matrice = [[0 for _ in range(len(allWords))] for __ in range(len(allFiles))] #ligne = document, colonne = mot

    for i in range(len(allFiles)):
        with open(directory+allFiles[i], "r", encoding="utf-8") as file:
            lines = file.readlines()
        freq = create_dictTFScore(''.join(lines))
        dictIDF = create_dictIDFScore(''.join(lines))
        for j in range(len(allWords)):
            if allWords[j] in freq:
                matrice[i][j] = round(freq[allWords[j]] * dictIDF[allWords[j]], 2)
    
    matriceTransposee = [[matrice[j][i] for j in range(len(matrice))] for i in range(len(matrice[0]))] # ligne = mot, colonne = document
    return matriceTransposee, allWords

def partie1():
    actionIsInt = False
    while not(actionIsInt):
        action = input("""\nQue voulez-vous faire ?
(0. Quitter)
1. Afficher les mots les moins importants
2. Afficher les mots au score TF-IDF le plus élevé
3. Indiquer les mots les plus répétés par Chirac
4. Indiquer les noms des présidents qui ont parlé de la « Nation » et celui qui l’a répété le plus de fois
5. Indiquer le premier président à parler du climat et/ou de l’écologie
6. Afficher les mots que tous les présidents ont utilisés (hormis non-importants)
> """)
        print()
        
        actionIsInt = (48 <= ord(action) <= 54)
        if not actionIsInt:
            print("Veuillez entrer un nombre entier compris entre 0 et 6.\n")
    
    action = int(action)
    matriceTFIDF, allWords = create_matriceTFIDF_and_allWords("cleaned\\")
    unsortedPresidents = list_of_presidents("speeches\\")
    
    while action != 0:
        match action:
            case 1: # Afficher les mots les moins importants
                print("Les mots les moins importants sont :")
                for i in range(len(allWords)):
                    if not(False in [matriceTFIDF[i][k] in [0, 1] for k in range(len(matriceTFIDF[i]))]): # remplit la condition seulement si tous les éléments de la ligne sont 0 ou 1
                        print(allWords[i], end=", ")
                print()
                
            case 2: # Afficher les mots au score TF-IDF le plus élevé
                motsScoreMax = {str(k): 0 for k in range(10)}
                for j in range(len(matriceTFIDF)):
                    scoreTFIDF_moyenne = round(sum(matriceTFIDF[j])/len(matriceTFIDF[j]), 2)
                    listeValeurs_motsScoreMax = list(motsScoreMax.values())
                    listeCles_motsScoreMax = list(motsScoreMax.keys())
                    listeItems_motsScoreMax = list(motsScoreMax.items())
                    if scoreTFIDF_moyenne > min(listeValeurs_motsScoreMax):
                        i = 0
                        while listeValeurs_motsScoreMax[i] >= scoreTFIDF_moyenne:
                            i += 1    
                        listeItems_motsScoreMax = listeItems_motsScoreMax[:i] + [(allWords[j], scoreTFIDF_moyenne)] + listeItems_motsScoreMax[i:-1]
                    motsScoreMax = dict(listeItems_motsScoreMax)
                
                print("Les 10 mots au score TF-IDF le plus élevé sont : ", end="")
                for word in listeCles_motsScoreMax[:-1]:
                    print(word, end=", ")
                print(listeCles_motsScoreMax[-1])
                
            case 3: # Indiquer les mots les plus répétés par Chirac
                motsChirac = {str(k): 0 for k in range(10)}
                
                for j in range(len(matriceTFIDF)):
                    scoreTFIDF_moyenne = round((matriceTFIDF[j][1]+matriceTFIDF[j][2])/2, 2)
                    listeValeurs_motsChirac = list(motsChirac.values())
                    listeCles_motsChirac = list(motsChirac.keys())
                    listeItems_motsChirac = list(motsChirac.items())
                    if scoreTFIDF_moyenne > min(listeValeurs_motsChirac):
                        i = 0
                        while listeValeurs_motsChirac[i] >= scoreTFIDF_moyenne:
                            i += 1    
                        listeItems_motsChirac = listeItems_motsChirac[:i] + [(allWords[j], scoreTFIDF_moyenne)] + listeItems_motsChirac[i:-1]
                    motsChirac = dict(listeItems_motsChirac)
                
                print("Les 10 mots les plus répétés par Chirac sont : ", end="")
                for word in listeCles_motsChirac[:-1]:
                    print(word, end=", ")
                print(listeCles_motsChirac[-1])
            
            case 4: # Indiquer les noms des présidents qui ont parlé de la « Nation » et celui qui l’a répété le plus de fois
                presidentsNation = []
                maxi = 0
                ligneMatriceNation = matriceTFIDF[allWords.index("nation")]
                for i in range(len(ligneMatriceNation)):
                    if ligneMatriceNation[i] != 0 and unsortedPresidents[i] not in presidentsNation:
                        presidentsNation.append(unsortedPresidents[i])
                    if ligneMatriceNation[i] > ligneMatriceNation[maxi]:
                        maxi = i
                
                print("Les présidents qui ont parlé de la « Nation » sont :", ', '.join(presidentsNation))
                print("Celui qui l'a le plus répété est", unsortedPresidents[maxi])
            
            case 5: # Indiquer le premier président à parler du climat et/ou de l’écologie
                chronologiePresidents = ['Giscard dEstaing', 'Mitterrand', 'Chirac', 'Sarkozy', 'Hollande', 'Macron']
                ligneMatriceClimat = matriceTFIDF[allWords.index("climat")]
                ligneMatriceEcologie = matriceTFIDF[allWords.index("écologique")] # car le mot "écologie" n'est jamais mentionné
                
                presidentsVert = []
                
                for i in range(len(ligneMatriceClimat)):
                    if (unsortedPresidents[i] not in presidentsVert) and (ligneMatriceEcologie[i] != 0 or ligneMatriceClimat[i] != 0):
                        presidentsVert.append(unsortedPresidents[i])

                i = 0
                while i < len(chronologiePresidents) and chronologiePresidents[i] not in presidentsVert:
                    i += 1 # parcourt la liste chronologique des présidents jusqu'à trouver le premier qui a parlé du climat
                print("Le premier président à parler du climat et/ou de l'écologie est", chronologiePresidents[i])
                
            case 6: # Afficher les mots que tous les présidents ont utilisés
                print("Les mots que tous les présidents ont utilisés sont : ", end="")
                for i in range(len(matriceTFIDF)):
                    nouvelleLigneMatrice = [matriceTFIDF[i][0]+matriceTFIDF[i][1], matriceTFIDF[i][2], matriceTFIDF[i][3], matriceTFIDF[i][4], matriceTFIDF[i][5]+matriceTFIDF[i][6], matriceTFIDF[i][7]] # on regroupe les discours de Giscard et de Mitterrand
                    if not(0 in nouvelleLigneMatrice):
                        print(allWords[i], end=", ")
                print()
                    
        actionIsInt = False
        while not(actionIsInt):
            action = input("""\nQue voulez-vous faire ?
(0. Quitter)
1. Afficher les mots les moins importants
2. Afficher les mots au score TF-IDF le plus élevé
3. Indiquer les mots les plus répétés par Chirac
4. Indiquer les noms des présidents qui ont parlé de la « Nation » et celui qui l’a répété le plus de fois
5. Indiquer le premier président à parler du climat et/ou de l’écologie
6. Afficher les mots que tous les présidents ont utilisés (hormis non-importants)
> """)
            print()
            
            actionIsInt = (48 <= ord(action) <= 54)
            if not actionIsInt:
                print("Veuillez entrer un nombre entier compris entre 0 et 6.\n")



def listOfWords(string):
    # Retourne la liste des mots d'une phrase
    for i in range(len(string)):
        if not(97 <= ord(string[i]) <= 122 or 65 <= ord(string[i]) <= 90):
            string = string[:i] + " " + string[i+1:]
        elif 65 <= ord(string[i]) <= 90:
            string = string[:i] + chr(ord(string[i]) + (97-65)) + string[i+1:]
    return string.split()

def listOfCommonElements(list1, list2):
    # Retourne la liste des éléments communs à deux listes
    return [e for e in list1 if e in list2]

def vecteurTFIDF(wordsList, allWords):
    # Retourne le vecteur TF-IDF d'une liste de mots
    vecteur = [0 for _ in range(len(allWords))]
    dictTF = create_dictTFScore(' '.join(wordsList))
    dictIDF = create_dictIDFScore(' '.join(wordsList))
    for word in wordsList:
        if word in allWords:
            vecteur[allWords.index(word)] = round(dictTF[word] * dictIDF[word], 2)
    return vecteur

def produitScalaire(vecteur1, vecteur2):
    # Retourne le produit scalaire de deux vecteurs
    somme = 0
    for i in range(len(vecteur1)):
        somme += vecteur1[i] * vecteur2[i]
    return somme

def norme(vecteur):
    # Retourne la norme d'un vecteur
    somme = 0
    for i in range(len(vecteur)):
        somme += vecteur[i]**2
    return round(sqrt(somme), 2)

def similarite(vecteur1, vecteur2):
    # Retourne la similarité cosinus de deux vecteurs
    return round(produitScalaire(vecteur1, vecteur2) / (norme(vecteur1) * norme(vecteur2)), 2)

def partie2():
    question = input("\nVotre question : ")
    words_in_question = listOfWords(question)
    matriceTFIDF, allWords = create_matriceTFIDF_and_allWords("cleaned\\")
    words_in_matrix = listOfCommonElements(allWords, words_in_question)
    vecteurQuestion = vecteurTFIDF(words_in_question, allWords)
    matriceTFIDF_transposee = [[matriceTFIDF[j][i] for j in range(len(matriceTFIDF))] for i in range(len(matriceTFIDF[0]))]
    
    
    
if __name__ == "__main__":
    cleanSpeeches()
    #partie1()
    partie2()