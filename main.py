from math import log10, sqrt
from os import listdir
from time import time
from random import choice
 
def list_of_files(directory, extension):
    # Retourne la liste des fichiers d'un répertoire d'une certaine extension
    return [filename for filename in listdir(directory) if filename.endswith(extension)] 

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
                if s[i] in ["-", "\n", "'", " "]: # caractères spéciaux a remplacer par un espace
                    s = s[:i] + " " + s[i+1:]
                    i += 1
                elif i != len(s)-1 and s[i-1:i+1] == "  ": # 2 espaces consécutifs
                    s = s[:i-1] + s[i:]
                elif not (65 <= ord(s[i]) <= 90 or 97 <= ord(s[i]) <= 122) and s[i] not in ["ç", "é", "è", "ê", "à", "â", "û", "Ç", "É", "È", "À", "Â"]: # autres caractères spéciaux
                    s = s[:i] + s[i+1:]
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
    for i in range(len(string)):
        if not(97 <= ord(string[i]) <= 122 or 65 <= ord(string[i]) <= 90) and string[i] not in ["ç", "é", "è", "ê", "à", "â", "û"]:
            string = string[:i] + " " + string[i+1:]
        elif 65 <= ord(string[i]) <= 90:
            string = string[:i] + chr(ord(string[i]) + (97-65)) + string[i+1:]
    words = string.split()
    frequency = {}
    for word in words:
        if word not in frequency:
            frequency[word] = 0
        frequency[word] += 1
    return frequency

def create_dictIDFScore(string):
    # Retourne un dictionnaire avec les mots et leur score IDF
    freq = create_dictTFScore(string)
    return {word : round(log10(len(string.split()) / freq[word]) + 1, 2) for word in freq}

def create_matriceTFIDF_and_allWords(directory):
    # Retourne un tuple contenant: 
    #  - la matrice de scores TF-IDF, où chaque ligne correspond à un mot et chaque colonne va avec un fichier du dossier 'cleaned'
    #  - la liste de tous les mots existants dans tous les fichiers
    allFiles = list_of_files(directory, ".txt")
    allWords = []
    for f in allFiles: #creation de la liste allWords
        with open(directory+f, "r", encoding="utf-8") as file:
            lines = file.read()
        for w in lines.split():
            if w not in allWords and len(w) > 3: # on considere que les mots de trois lettres ou moins sont non-importants
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

def partie1(matriceTFIDF, allWords):
    optionIsInt = False
    while not(optionIsInt):
        option = input("""\nQue voulez-vous faire ?
(0. Quitter)
1. Afficher les mots les moins importants
2. Afficher les mots au score TF-IDF le plus élevé
3. Indiquer les mots les plus répétés par Chirac
4. Indiquer les noms des présidents qui ont parlé de la « Nation » et celui qui l’a répété le plus de fois
5. Indiquer le premier président à parler du climat et/ou de l’écologie
6. Afficher les mots que tous les présidents ont utilisés (hormis non-importants)
> """)
        print()
        
        optionIsInt = len(option) == 1 and (48 <= ord(option) <= 54)
        if not optionIsInt:
            print("Veuillez entrer un nombre entier compris entre 0 et 6.\n")
    
    option = int(option)
    unsortedPresidents = list_of_presidents("speeches\\")
    
    match option:
        case 1: # Afficher les mots les moins importants
            print("Les mots les moins importants sont :")
            for i in range(len(allWords)):
                if not(False in [matriceTFIDF[i][k] < 4 for k in range(len(matriceTFIDF[i]))]): # remplit la condition seulement si tous les éléments de la ligne sont inférieurs à 3
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
        



def listOfWords(string):
    # Retourne la liste des mots d'une phrase
    for i in range(len(string)):
        if not(97 <= ord(string[i]) <= 122 or 65 <= ord(string[i]) <= 90) and string[i] not in ["ç", "é", "è", "ê", "à", "â", "û"]:
            string = string[:i] + " " + string[i+1:]
        elif 65 <= ord(string[i]) <= 90:
            string = string[:i] + chr(ord(string[i]) + (97-65)) + string[i+1:]
    return string.split(' ')

def listOfCommonElements(list1, list2):
    # Retourne la liste des éléments communs à deux listes
    return [e for e in list1 if e in list2]

def vecteurTFIDF(matriceTFIDF, wordsList, question, allWords):
    # Retourne le vecteur TF-IDF d'une liste de mots
    vecteur = [0 for _ in range(len(allWords))]
    freq = create_dictTFScore(question)
    wordsFound = 0
    i = 0
    while wordsFound < len(wordsList):
        if allWords[i] in wordsList:
            vecteur[i] = round(freq[allWords[i]] * sum(matriceTFIDF[i]) / len(matriceTFIDF[i]), 2)
            wordsFound += 1
        i += 1
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

def documentLePlusPertinent(vecteur, matrice, fichiers):
    # Retourne le nom du document le plus pertinent par rapport à un vecteur
    similarites = []
    maxi = 0
    for i in range(len(matrice)):
        similarites.append(similarite(vecteur, matrice[i]))
        if similarites[i] > similarites[maxi]:
            maxi = i
    return fichiers[maxi]

def indice_motTFIDFMaximumDansVecteur(vecteur):
    # Retourne le mot du vecteur qui a le score TF-IDF le plus élevé
    max_index = 0
    for i in range(len(vecteur)):
        if vecteur[i] > vecteur[max_index]:
            max_index = i
    return max_index

def phraseDontApparitionMot(mot, repertoire, fichier):
    # Retourne la premiere phrase d'un fichier dans lequel apparait un mot
    with open(repertoire+fichier, "r", encoding="utf-8") as file:
        lines = file.readlines()
    for line in lines:
        if ' ' + mot + ' ' in line.lower():
            return line
    return ''

def questionStarter():
    # Retourne le début d'une réponse à une question
    return choice(["D'après mes sources, ", "Selon mes informations, ", "D'après mes recherches, ", "Selon mes connaissances, ", "Bien sûr, ", "Bien entendu, "])

def partie2(matriceTFIDF, allWords):
    question = input("\nVotre question : ")
    words_in_question = listOfWords(question)
    words_in_matrix = listOfCommonElements(words_in_question, allWords)
    if words_in_matrix == []: # aucun mot de la question n'est dans la matrice
        return "Désolé, aucun document ne correspond à votre question."        
    vecteurQuestion = vecteurTFIDF(matriceTFIDF, words_in_matrix, question, allWords)
    matriceTFIDF_transposee = [[matriceTFIDF[j][i] for j in range(len(matriceTFIDF))] for i in range(len(matriceTFIDF[0]))] #ligne = document, colonne = mot
    documentAdapte = documentLePlusPertinent(vecteurQuestion, matriceTFIDF_transposee, list_of_files("cleaned\\", ".txt"))
    motLePlusPertinent = allWords[indice_motTFIDFMaximumDansVecteur(vecteurQuestion)]
    debutReponse = questionStarter()
    reponse = phraseDontApparitionMot(motLePlusPertinent, "speeches\\", documentAdapte)
    if reponse == '':
        return 'Désolé, je n\'ai pas trouvé de phrase dans laquelle apparaît le mot "' + mot + '".'
    if 65 <= ord(reponse[0]) <= 90: # supprime la majuscule au debut de "reponse", car "debutReponse" vient avant
        reponse = chr(ord(reponse[0]) + (97-65)) + reponse[1:]
    return debutReponse + reponse

if __name__ == "__main__":
    cleanSpeeches()
    matriceTFIDF, allWords = create_matriceTFIDF_and_allWords("cleaned\\")
    
    action = -1
    while action != 0:
        actionIsInt = False
        while not actionIsInt:
            action = input("\nQuelle partie voulez-vous lancer ? (1 ou 2, 0 pour quitter) :\n > ")
            actionIsInt = len(action) == 1 and (48 <= ord(action) <= 51)
            if not actionIsInt:
                print("Veuillez entrer un nombre entier compris entre 0 et 2.\n")
        action = int(action)
        
        if action == 1:
            partie1(matriceTFIDF, allWords)
        elif action == 2: # pas un else car action peut etre 0
            print('\n', partie2(matriceTFIDF, allWords))