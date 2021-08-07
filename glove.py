# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 09:36:50 2019

@author: Théodore Chapuis-Chkaiban
"""

#Numpy pour la manipulation des tableaux
import numpy as np

#Sql pour la gestion des bases de données
import sqlite3 as sql

#re pour la gestion des chaînes de caractère (voir après)
import re

#random pour mélanger les éléments d'une liste
import random


"""db = '../input/enwiki-20170820.db' """


#Liens vers les bases de données (il faut modifier les chemins)
db_wikipedia = r"C:\Users\theod\Desktop\tipe\Wikipedia_dataset\input\enwiki20170820.db"

path = r"C:\Users\theod\Desktop\glove_trained_by_int\save\{}"

db_cooccurences = path.format("Cooccurences.db")
db_lmots = path.format("l_mots.db")

db_dico_mots = path.format("dico_mots.db") #Permet la sauvegarde simultanée de di_mots et dm_mots

db_vect_mots = path.format("vect_mots.db")
db_vect_context = path.format("vect_context.db")
db_vect_mots_grad_hist = path.format("vect_mots_grad_hist.db")
db_vect_context_grad_hist = path.format("vect_context_grad_hist.db")
db_bias_mots = path.format("bias_mots.db")
db_bias_context = path.format("bias_context.db")
db_bias_mots_grad_hist = path.format("bias_mots_grad_hist.db")
db_bias_context_grad_hist = path.format("bias_context_grad_hist.db")

######################################################################################

#DECLARATION DES VARIABLES GLOBALES

# Un tableau de tuple, chaque tuple contient l'indice de l'article lu (Coordonnée 0)
# et la liste des mots de l'article,

#Différentes sections d'un même article représentent deux tuples différents mais dont la 1e 
#coordonnée est la même

l_mots = [(0, [])]


#dictionnaires des mots: "mots"-> indices
dm_mots ={}
dm_mots["\n"] =0


#dictionnaire des indices: indices -> "mots"
di_mots ={}
di_mots[0] ="\n"

#Dictionnaire des cooccurences, chaque clef (mot principal) contient un tuple dont le 1e élément est le nombre
#d'apparitions (ou occurences) du mot principal et dont le 2nd élément est lui-meme un dictionnaire
#dont les clefs sont les mots de contexte associés au mot principal. Chaque clef de ce second dictionnaire
# contient le nombre d'occurrences du couple (mot principal / mot contexte)

Cooccurences = {}

#Cette variable contient le nombre d'articles à parcourir pour l'entrainement de l'algorithme
nb_articles = 1000

#Nombre de mots distincts dans le texte à lire (ie l'ensemble des textes des divers articles)
nb_mots = 0

# Profondeur de champ (taille des phrases lues ie l'algorithme lit c-mots en avant et c-mots en arrière du mot principal)
c = 3

nb_articles_total = 23046187 #pour éviter d'avoir à le recalculer

##############################
# Pour la phase d'entrainement            

#Matrice vecteurs/mots_principaux
word_vect_matrix = np.array(0)

#Matrice vecteurs/contextes
context_vect_matrix = np.array(0)

#Matrices des biais des mots principaux et des contextes
word_bias_array = np.array(0)
context_bias_array = np.array(0)

#Matrices d'enregistrement de l'historique des gradients (méthode AdaGrad)
word_grad_history = np.array(0)
context_grad_history = np.array(0)
word_bias_grad_history = 1
context_bias_grad_history = 1

N = 100 # Dimension des vecteurs

f_app = 0.5 # Facteur d'apprentissage

iteration = 1 #Nombre d'itérations

#Facteurs de la fonction de coût
alpha = 3/4
x_max = 100 


############################################################################################

#Création des bases de données nécessaires à la sauvegarde

#Cooccurences :

def creation_db_cooc():
    
    connection_cooc = sql.connect(db_cooccurences) #On ouvre la base de données
    
    cursor_cooc = connection_cooc.cursor() #On récupère un curseur qui exécutera les instructions sql
    
    #Création de la table Cooccurences
    
    cursor_cooc.execute("""
    CREATE TABLE IF NOT EXISTS Cooccurences (
         id_cooc INTEGER PRIMARY KEY,
         moti VARCHAR,
         occurences INTEGER,
         motcont VARCHAR, 
         cooccurences NUMERIC(8,3)
    )
    """)
    
    
    connection_cooc.commit() #On enregistre les modifications
    
    connection_cooc.close() #On ferme la database
    
def creation_db_dico_mots():
    with sql.connect(db_dico_mots) as conn:
        
        cursor = conn.cursor()
        
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dico_mots (
         id_mot INTEGER PRIMARY KEY,
         mot VARCHAR
    )
    """)
        
        conn.commit()

#l_mots: idem
def creation_db_lmots():
    
    connection_lmots = sql.connect(db_lmots)
    
    cursor_lmots = connection_lmots.cursor()
    
    cursor_lmots.execute("""
    CREATE TABLE IF NOT EXISTS Lmots (
         id_mot INTEGER PRIMARY KEY,
         id_article INTEGER,
         mot VARCHAR)
            """)
    
    connection_lmots.commit()
    
    connection_lmots.close()

def init_db():
    creation_db_cooc()
    creation_db_dico_mots()
    creation_db_lmots()
#CREATION DES DB NECESSAIRES A L'ENREGISTREMENT DES VECTEURS

#vect_mots
def creation_db_vect_mots():
    
    connection_vect_mots = sql.connect(db_vect_mots)
    
    cursor_vect_mots = connection_vect_mots.cursor()
    
    cursor_vect_mots.execute("""
    CREATE TABLE IF NOT EXISTS Vect_mots (id_vect_mot INTEGER PRIMARY KEY, mot VARCHAR) """)
    
    connection_vect_mots.commit()  
    try:
        for i in range(N): #Pour rajouter les N coordonnées des vecteurs
            create_sql = ("""ALTER TABLE Vect_mots
                              ADD coordonnee_{ni} NUMERIC (8,5)
                              """)
            create = create_sql.format(ni = i)
            cursor_vect_mots.execute(create)
            
    except:
        print("Already exists")
          
    connection_vect_mots.close()
    
def creation_db_vect_context():
    
    with sql.connect(db_vect_context) as connection_vect_context:
            
        cursor_vect_context = connection_vect_context.cursor()
        
        cursor_vect_context.execute("""
        CREATE TABLE IF NOT EXISTS Vect_context (id_vect_context INTEGER PRIMARY KEY, context VARCHAR) """)
        
        connection_vect_context.commit()
        try:            
            for i in range(N):
                create_sql = ("""ALTER TABLE Vect_context
                              ADD coordonnee_{ni} NUMERIC (8,5)
                              """)
                create = create_sql.format(ni = i)
                cursor_vect_context.execute(create)
        except:
            print("Already exists")



def creation_db_vect_mots_grad_hist():
    
    with sql.connect(db_vect_mots_grad_hist) as connection_vect_mots_grad_hist:
            
        cursor_vect_mots_grad_hist = connection_vect_mots_grad_hist.cursor()
        
        cursor_vect_mots_grad_hist.execute("""
        CREATE TABLE IF NOT EXISTS Vect_mots_grad_hist (id_vect_mots INTEGER PRIMARY KEY, mot VARCHAR """)
        
        connection_vect_mots_grad_hist.commit()
        try:          
            for i in range(N):
                create_sql = ("""ALTER TABLE Vect_mots_grad_hist
                              ADD coordonnee_{ni} NUMERIC (8,5)
                              """)
                create = create_sql.format(ni = i)
                cursor_vect_mots_grad_hist.execute(create)
        except:
            print("Already exists")

def creation_db_vect_context_grad_hist():
    
    with sql.connect(db_vect_context_grad_hist) as connection_vect_context_grad_hist:
            
        cursor_vect_context_grad_hist = connection_vect_context_grad_hist.cursor()
        
        cursor_vect_context_grad_hist.execute("""
        CREATE TABLE IF NOT EXISTS Vect_context_grad_hist (id_vect_context INTEGER PRIMARY KEY, context VARCHAR) """)
        
        connection_vect_context_grad_hist.commit()
        try: 
            for i in range(N):
                create_sql = ("""ALTER TABLE Vect_context_grad_hist
                              ADD coordonnee_{ni} NUMERIC (8,5)
                              """)
                create = create_sql.format(ni = i)
                cursor_vect_context_grad_hist.execute(create)
        except:
            print("Already exists")

def creation_db_bias_mot():
    
        with sql.connect(db_bias_mots) as connection_bias_mots:
            cursor_bias_mots = connection_bias_mots.cursor()
            
            cursor_bias_mots.execute("""
            CREATE TABLE IF NOT EXISTS Bias_mot(id_mot INTEGER PRIMARY KEY, mot VARCHAR, bias NUMERIC(8,5)) """ )
            
            connection_bias_mots.commit()

def creation_db_bias_context():
    
        with sql.connect(db_bias_context) as connection_bias_context:
            cursor_bias_context = connection_bias_context.cursor()
            
            cursor_bias_context.execute("""
            CREATE TABLE IF NOT EXISTS Bias_context(id_context INTEGER PRIMARY KEY, context VARCHAR, bias NUMERIC(8,5)) """ )
            
            connection_bias_context.commit()

def create_db_vect():
    creation_db_vect_mots()
    creation_db_vect_context()
    creation_db_bias_mot()
    creation_db_bias_context()    


def create_all():
    init_db()
    create_db_vect()
    
    

#Fin de la création des bases de données

########################################################################################

#Enregistrement et lecture des bases de données


# On écrit ici les fonctions utilisées pour enregistrer les données

def save_lmots(): #Pour sauvegarder l_mots dans la database Lmots, suite à la lecture de Wikipédia
    global l_mots 
    
    with sql.connect(db_lmots) as connection_lmots: #Cette ligne permet de se connecter à la database db_lmots
        cursor_lmots = connection_lmots.cursor()
        
        i = 0        
        
        for (index, texte) in l_mots:
            for mot in texte:                
                
                insertion_sql = '''INSERT INTO Lmots(id_mot, id_article, mot)
                VALUES(NULL, {ind}, '{word}') '''
                insertion = insertion_sql.format(ind = index, word = mot)
                
                #"format" permet de compléter l'intérieur des {}
                
                cursor_lmots.execute(insertion)
                
            i += 1
            if i % 10000 == 0:
                print(i)
        
        connection_lmots.commit() #on enregistre
        
    # à l'issue du with, la database se ferme automatiquement (pas besoin de mettre connection_lmots.close())
    
def save_cooccurences(): #pareil pour les cooccurences
    global Cooccurences
    
    with sql.connect(db_cooccurences) as connection_cooc:
        
        cursor_cooc = connection_cooc.cursor()

        i = 0
        for moti in Cooccurences.keys(): #avec .keys() on récupère la liste des clefs du dictionnaire
            
            if Cooccurences[moti][0] == -1: #on enregistre pas les vecteurs qui sont apparus trop de fois
                continue
            
            for motj in Cooccurences[moti][1].keys():
                insertion_sql = '''INSERT INTO Cooccurences(id_cooc, moti, occurences, motcont, cooccurences) VALUES(NULL, '{motind}', {occ}, '{motcont}', {cooc})'''
                insertion = insertion_sql.format(motind = moti, occ = Cooccurences[moti][0], motcont = motj, cooc = Cooccurences[moti][1][motj])
                cursor_cooc.execute(insertion)
            
            i+=1
            if i % 1000 == 0:
                print(i)
            
            
        connection_cooc.commit()
        
def save_dico_mots():
    global di_mots
    
    with sql.connect(db_dico_mots) as conn:
        cursor = conn.cursor()
        
        for index in di_mots.keys():
            insertion_sql = '''INSERT INTO Dico_mots VALUES(NULL, '{mot}')'''
            insertion = insertion_sql.format(mot = di_mots[index])
            cursor.execute(insertion)
            
        conn.commit()

        
        
def save_vect_mots():
    global word_vect_matrix
    
    with sql.connect(db_vect_mots) as connection_vect_mots:
        cursor_vect_mots = connection_vect_mots.cursor()
        
        for (i,vect_mot) in enumerate(word_vect_matrix):
            
            mot = di_mots[i]
            
            insertion_sql = '''INSERT INTO Vect_mots VALUES(NULL, '{m}', {values})'''
            
            val = ', '.join(map(str, vect_mot)) #On traite la liste des coordonnées pour les afficher en format string,
                                                #les éléments étant séparés par des virgules            
            insertion = insertion_sql.format(m = mot, values = val)
            
            cursor_vect_mots.execute(insertion)
            
            if i % 100000 == 0:
                print(i)
            
        connection_vect_mots.commit()
            
        
def save_vect_context():
    global context_vect_matrix
    
    with sql.connect(db_vect_context) as connection_vect_context:
        cursor_vect_context = connection_vect_context.cursor()
        
        for (i,vect_context) in enumerate(context_vect_matrix):
            
            mot = di_mots[i]
            
            insertion_sql = '''INSERT INTO Vect_context VALUES(NULL, '{m}', {values})'''
            
            val = ', '.join(map(str, vect_context)) #On traite la liste des coordonnées pour les afficher en format string,
                                                #les éléments étant séparés par des virgules            
            insertion = insertion_sql.format(m = mot, values = val)
            
            cursor_vect_context.execute(insertion)
            
            if i % 100000 == 0:
                print(i)
            
        connection_vect_context.commit()
        
def save_word_bias():
    global word_bias_array
    
    with sql.connect(db_bias_mots) as conn:
        cursor = conn.cursor()
        
        for (i, bias) in enumerate(word_bias_array):
            
            mot = di_mots[i]
            
            insertion_sql = '''INSERT INTO Bias_mot VALUES(NULL, '{m}', {value})'''       
            insertion = insertion_sql.format(m = mot, value = bias)
            
            cursor.execute(insertion)
            
        conn.commit()

def save_context_bias():
    global context_bias_array
    
    with sql.connect(db_bias_context) as conn:
        cursor = conn.cursor()
        
        for (i, bias) in enumerate(context_bias_array):
            
            mot = di_mots[i]
            
            insertion_sql = '''INSERT INTO Bias_context VALUES(NULL, '{m}', {value})'''       
            insertion = insertion_sql.format(m = mot, value = bias)
            
            cursor.execute(insertion)
            
        conn.commit()
        
def save_reading():
    save_lmots()
    save_cooccurences()
    save_dico_mots()
        
def save_training():
    save_vect_mots()
    save_vect_context()
    save_word_bias()
    save_context_bias()
    
def save():
    save_reading()
    save_training()

def save_int():
    save_cooccurences()
    save_dico_mots()
    save_training()

#On souhaite maintenant lire les données enregistrées

def read_lmots():
    
    with sql.connect(db_lmots) as connection_lmots:
        cursor_lmots = connection_lmots.cursor()
        lmots_c = cursor_lmots.execute('''SELECT id_article, mot FROM Lmots''')
        
        #les trois variables suivantes permetteront de localiser les changements d'articles
        #en effet on souhaite préserver la structure de l_mots et donc obtenir un tuple par article
        
        liste_textes = []
        id0 = (lmots_c.fetchone())[0] # permet de récupérer le premier élément de la requête sql
        texte0 = []
        
        for (i, (idt , mot)) in enumerate(lmots_c): #on parcourt la requête sql
            
            if idt == id0: #quand les mots appartiennent toujours au même article on ne fait que les ajouter
                texte0.append(mot)  # au texte de l'article
            else:
                liste_textes.append((id0, texte0))  #sinon on enregistre l'article et on passe au suivant
                id0 = idt
                texte0 = [mot]
            
            if i%1000000 == 0:
                print(i)
            
            
        liste_textes.append((id0,texte0)) #on ajoute le dernier article
        
    return liste_textes #pas de problème d'alias car liste_textes est locale
    
def read_cooccurences(): #même principe
    cooccurences = {}
    
    with sql.connect(db_cooccurences) as connection_cooc:
        cursor_cooc = connection_cooc.cursor()
        cooc_c = cursor_cooc.execute('''SELECT moti, occurences, motcont, cooccurences FROM Cooccurences''')
                
        (mot0, occ0) = (cooc_c.fetchone())[0:2]
        context0 = {}
        
        for (i, (moti , occ, motcont, cooc)) in enumerate(cooc_c):
            if moti == mot0:
                context0[motcont] = cooc 
            else:
                cooccurences[mot0] = (occ0, context0)
                
                context0 = {}
                context0[motcont] = cooc
                
                (mot0, occ0) = (moti, occ)
            if i%1000000 == 0:
                print(i)   
            
        cooccurences[moti] = (occ, context0)
    return cooccurences

def read_dico_mots(): #permet de récupérer dm_mots et di_mots
    dm_mots = {}
    di_mots = {}
    
    with sql.connect(db_dico_mots) as conn:
        cursor = conn.cursor()
        
        dico_c = cursor.execute('''SELECT * FROM Dico_mots''')
        
        for (index, mot) in dico_c:
            dm_mots[mot] = index
            di_mots[index] = mot
            
    return (dm_mots, di_mots)

def read_vect_mots():
    
    with sql.connect(db_vect_mots) as connection_vect_mots:
        cursor_vect_mots = connection_vect_mots.cursor()
        vect_mots_c = cursor_vect_mots.execute('''SELECT * FROM Vect_mots''')
        
        vect0 = (vect_mots_c.fetchone()[1:]) #on ne retient pas l'indice 0 qui est l'identifiant (INTEGER PRIMARY KEY)
        word_vect_mat = np.array(vect0) #on initialise la matrice
        
        for (i, vect) in enumerate(vect_mots_c):
            
            if i == 0:
                continue #on a déjà mis le premier vecteur
            
            word_vect_mat.append(vect[1:])
        
        return word_vect_mat
    
def read_vect_context():
    
    with sql.connect(db_vect_mots) as connection_vect_context:
        cursor_vect_context = connection_vect_context.cursor()
        vect_context_c = cursor_vect_context.execute('''SELECT * FROM Vect_context''')
        
        vect0 = (vect_context_c.fetchone()[1:]) #on ne retient pas l'indice 0 qui est l'identifiant (INTEGER PRIMARY KEY)
        context_vect_mat = np.array(vect0) #on initialise la matrice
        
        for (i, vect) in enumerate(vect_context_c):
            
            if i == 0:
                continue #on a déjà mis le premier vecteur
            
            context_vect_mat.append(vect[1:])
        
        return context_vect_mat
    
def read_docs():
    global Cooccurences
    global l_mots
    global dm_mots
    global di_mots
    
    global word_vect_matrix
    global context_vect_matrix
    
    Cooccurences = read_cooccurences()
    l_mots = read_lmots()
    (dm_mots, di_mots) = read_dico_mots()
    word_vect_matrix = read_vect_mots()
    context_vect_matrix = read_vect_context()
    

#########################################################################################

#LECTURE ET TRAITEMENT DES DONNEES EN AMONT


def nombre_articles(): #Requête pour récupérer le nombre total d'articles
    
    #On récupère le nombre total d'articles
    with sql.connect(db_wikipedia) as conn:
        cursor = conn.cursor()
        count = cursor.execute('''SELECT COUNT(*) FROM articles''')
        
        nb_total = count.fetchall()[0]
    return nb_total[0]

def random_array(binf = 0, bsup = nb_articles_total, sel = nb_articles): #Créée une liste aléatoire de taille (bsup-binf) et dont les éléments sont des
    #entiers compris entre binf et bsup
    array = np.floor((bsup - binf) * np.random.rand(sel) + binf)
    return (array).astype(int)
        

def get_query(select, db=db_wikipedia):
    # permet de récupérer une requête et les noms des colones de la requête
    with sql.connect(db) as conn:
        c = conn.cursor()
        c.execute(select)
        col_names = [str(name[0]).lower() for name in c.description]
    return c.fetchall(), col_names

def tokenize(text, lower=True):
    #Permet de transformer le texte d'un article en liste de mots,
    # Elimine les apostrophes, ne garde que les lettres de l'alphabet et les underscore
    # Lorsque lower=True le texte est transformé en minuscule
    
    text = re.sub("'", "", text)
    if lower:
        tokens = re.findall('''[a-z]+''', text.lower())
    else:
        tokens = re.findall('''[A-Za-z]''', text)
    return tokens

def get_article(article_id):
    #Pour selectionner un article uniquement
    select = '''select section_text from articles where article_id=%d''' % article_id
    docs, _ = get_query(select)
    docs = [doc[0] for doc in docs]
    doc = ' '.join(docs)
    tokens = tokenize(doc)
    return tokens

def get_wiki_interval(inf = 0, sup = nb_articles_total, sel = nb_articles):
    
    #Selectionne "sel" articles choisis parmi l'ensemble des articles
    #dont l'id est compris entre inf et sup
    #Renvoie une liste de tuples qui contiennent l'Id de l'article et le texte de la section concernée
    #Si random = True, renvoie un ensemble de "sel" articles sélectionnés dans un ordre aléatoire dont
    #l'id est compris entre inf et sup; par défaut vaut False
    
    select = '''select article_id, section_text from articles where article_id in ({list})'''
    
    if random:
        array = map(str,(random_array(inf,sup, sel)))

    else:
        array = map(str, range(inf, sup, int((sup-inf)/sel)))
        
    select = select.format( list = (', '.join(array)))
    
    docs, _ = get_query(select)
    
    docs = [(doc[0], tokenize(doc[1])) for doc in docs]
    
    return docs


def init_lmots_interval(inf, sup, sel): # Pour initialiser l_mots
    global l_mots
    l_mots = get_wiki_interval(inf, sup, sel)


def lecture(): # Lit l_mots et construit dm_mots, di_mots, et initialise Cooccurences
    global nb_mots
    global l_mots # Nécessite d'avoir déjà initialisé l_mots
    for id_texte in l_mots :
    #si le mot n'a jamais été rencontré, il faut l'ajouter aux dictionnaires
        for mot in id_texte[1]:
            if not mot in dm_mots:
                dm_mots[mot] = nb_mots
                di_mots[nb_mots]= mot
                Cooccurences[mot] = [1,{}]
                nb_mots+=1   


#FIN DE LECTURE

#####################################################################################################
                
#Mise à jour des cooccurences et entraînement de l'algorithme

def majCooccurences():
    global Cooccurences
    
    for (counter,id_texte) in enumerate(l_mots) :
        for (i, moti) in enumerate(id_texte[1]):#l'intérêt de séparer les différents articles apparaît ici
                                                # cela permet de ne pas comparer les mots de la fin d'un article
                                                # avec ceux du début du suivant
            
            if Cooccurences[moti][0] == -1:
                continue
                                
            if Cooccurences[moti][0] > 100000: #lorsqu'un mot apparaît trop de fois, c'est certainement un mot de liaison 
                Cooccurences[moti][0] = -1       #peu utile pour les statistiques, on le supprime du dictionnaire
            
                continue
            
            Cooccurences[moti][0] +=1
            
            for j in range(1,c):
                if i - j >= 1: #pour éviter les questions d'indices
                    motj_avant = id_texte[1][i-j]
                    if not motj_avant in Cooccurences[moti][1] :
                        Cooccurences[moti][1][motj_avant] = 1/j    #On pondère l'importance du mot de contexte par l'inverse
                                                                    # de sa distance au mot principal
                    else :
                        Cooccurences[moti][1][motj_avant] += (1/j)
                
                if len(id_texte[1]) > i + j:
                    motj_apres = id_texte[1][i+j]
                    if not motj_apres in Cooccurences[moti][1] :
                        Cooccurences[moti][1][motj_apres] = 1/j
                    else :
                        Cooccurences[moti][1][motj_apres] += (1/j)
                        
        if ((counter/len(l_mots))*100) % 10 == 0 :
            print((counter/len(l_mots))*100)
               

# FIN DE MISE A JOUR DES COOCCURENCES
        
############################################################################################################
            
#Entraînement de l'algorithme
            


def normer_vect(m):
    u=0
    for j in m:
        u+=j**2
    return m/(u**0.5)
                
def normer(Mat):
    Mat_Norm = np.copy(Mat)
    for i in range(len(Mat)):
        m=Mat[i]
        Mat_Norm[i]=normer_vect(m)
    return Mat_Norm

def norm_unit(W):
    W_norm = np.zeros(W.shape)
    d = (np.sum(W ** 2, 1) ** (0.5))
    W_norm = (W.T / d).T
    return W_norm

def cost_fct (xij):
    global x_max
    global alpha
    
    if xij > x_max:
        return 1
    else:
        return np.power((xij/x_max),alpha)
    
def init_training():
    global word_vect_matrix
    global context_vect_matrix
    global word_bias_array
    global context_bias_array
    
    #On initialise les matrices aléatoirement
    word_vect_matrix = (np.random.rand(nb_mots, N) - 0.5) * (1/nb_mots)
    context_vect_matrix = (np.random.rand(nb_mots, N) -0.5) * (1/nb_mots)
    word_bias_array = (np.random.rand(nb_mots) - 0.5) * (1/nb_mots)
    context_bias_array = (np.random.rand(nb_mots) -0.5) * (1/nb_mots)
    
    
def adapt_training(): # Permet d'adapter les matrices des vecteurs/mots, vecteurs/contextes au nouveau nombre de mots
                    # Cela est essentiel quand on procède par tranches (on modifie le nombre de mots connus à chaque étape)
    global word_vect_matrix
    global context_vect_matrix
    global word_bias_array
    global context_bias_array
    
    global nb_mots
    
    if nb_mots > len(word_vect_matrix):
        
        randmat =  (np.random.rand((nb_mots - len(word_vect_matrix)), N) - 0.5) * (1/nb_mots) 
        randvec = (np.random.rand((nb_mots - len(word_bias_array))) - 0.5) * (1/nb_mots)
        
        word_vect_matrix = np.concatenate((word_vect_matrix, randmat), axis = 0)
        context_vect_matrix = np.concatenate((context_vect_matrix, randmat), axis = 0)
        
        word_bias_array = np.concatenate((word_bias_array, randvec), axis = 0)
        context_bias_array = np.concatenate((context_bias_array, randvec), axis = 0)
    
    
def training(shuffle = True, AdaGrad = True):
    global nb_mots
    global l_mots
    global dm_mots
    global iteration
    
    global word_vect_matrix
    global context_vect_matrix
    global word_bias_array
    global context_bias_array
    
    if AdaGrad:        
        
        global word_grad_history
        global context_grad_history
        global word_bias_grad_history
        global context_bias_grad_history
        
        #A chaque fois qu'on recommence une session de training on réinitialise l'historique des gradients pour éviter
        #d'avoir des gradients trop élevés (inconvénient de AdaGrad)
        
        word_grad_history = np.ones((nb_mots, N)) 
        context_grad_history = np.ones((nb_mots, N))
        word_bias_grad_history = np.ones(nb_mots)
        context_bias_grad_history = np.ones(nb_mots)
    
    
    
    if shuffle: # Permet de mélanger l_mots pour optimiser AdaGrad (par défaut vaut True)
        random.shuffle(l_mots)
        
    for (counter, (ida, article)) in enumerate(l_mots):
        
        for (i, moti) in enumerate(article):
            
            if (i+c)< len(article) and i-c >= 0:                
                for j in range(1,c):
                    
                    motcont = article[i-j]
                    
                    indice_moti = dm_mots[moti]
                    indice_motcont = dm_mots[motcont]
                    
                    vect_i = word_vect_matrix[indice_moti]
                    vect_cont = context_vect_matrix[indice_motcont]
                            
                    bias_i = word_bias_array[indice_moti]
                    bias_cont = context_bias_array[indice_motcont]
                    
                    for k in range(1, iteration): #itération pour effectuer plusieurs calculs
                        if motcont in Cooccurences[moti][1]:
                            
                            xij = Cooccurences[moti][1][motcont]
                            scalaire = np.dot(vect_i,vect_cont) + bias_i + bias_cont - np.log(xij)
                                                
                            ponderation = cost_fct(xij)
                            
                            dJ_moti = (ponderation * scalaire) * vect_i
                            dJ_motcont = (ponderation * scalaire) * vect_cont
                            dJ_bias_i = (scalaire * ponderation)
                            dJ_bias_cont = dJ_bias_i                    
                            
                            #On met à jour les vecteurs et les biais
                            
                            if AdaGrad: #True par défaut
                                vect_i = vect_i - f_app * (dJ_moti * 1/(np.sqrt(word_grad_history[indice_moti])))
                                vect_cont = vect_cont - f_app * (dJ_motcont * 1/(np.sqrt(context_grad_history[indice_motcont])))
                                bias_i -= f_app * dJ_bias_i / (np.sqrt(word_bias_grad_history[indice_moti]))
                                bias_cont -= f_app * dJ_bias_cont / (np.sqrt(context_bias_grad_history[indice_motcont]))
                                
                                #On met à jour l'historique des gradients (si AdaGrad)
                                word_grad_history[indice_moti] += np.power(dJ_moti,2)
                                context_grad_history[indice_motcont] += np.power(dJ_motcont,2)
                                word_bias_grad_history[indice_moti] += np.power(dJ_bias_i,2)
                                context_bias_grad_history[indice_motcont] += np.power(dJ_bias_cont,2)
                                
                            
                            
                            # # Méthode sans AdaGrad
                            else:    
                                vect_i -=f_app * dJ_moti 
                                vect_cont -= f_app * dJ_motcont
                                bias_i -= f_app * dJ_bias_i 
                                bias_cont -= f_app * dJ_bias_cont
                                
                            
                            
                    
                    
        if ((counter/len(l_mots))*100) % 10 == 0 :
            print((counter/len(l_mots))*100)
              
        
def train_by_interval(max_value = nb_articles_total, pas = 10000 , shuffle = True, AdaGrad = True):
    global l_mots
    global word_vect_matrix
    
    create_all()
    
    inter = int(max_value / pas)
    
    #il faut lancer la première étape séparément car on a besoin d'avoir nb_mots pour initialiser les
    #matrices de training (voir init_training)
    print("debut init_lmots")
    
    init_lmots_interval(0,pas, pas) 
    
    print("fin init_lmots")
    
    lecture()
        
    s = "fin de lecture de l'étape {i0} sur {i1}"
    print(s.format(i0 = 0, i1 = inter -1))
    majCooccurences()
    s = "fin mise a jour occurences de l'étape {i0} sur {i1}"
    print(s.format(i0 = 0, i1 = inter-1))
    
    init_training()
    
    training(shuffle, AdaGrad)
        
    s = "fin de training de l'étape {i0} sur {i1}"
    print(s.format(i0 = 0, i1 = inter-1))
        
    #On reset seulement l_mots pour éviter les surcharges
        
    l_mots = [(0, [])]
    
    for i in range(1, inter):
        
        init_lmots_interval(i*pas,(i+1)*pas, pas)
        
        lecture()
        
        s = "fin de lecture de l'étape {i0} sur {i1}"
        print(s.format(i0 = i, i1 = inter -1))
        
        majCooccurences()
        s = "fin mise a jour occurences de l'étape {i0} sur {i1}"        
        print(s.format(i0 = i, i1 = inter -1))
        
        adapt_training()
        
        training(shuffle, AdaGrad)
        
        s = "fin de training de l'étape {i0} sur {i1}"
        print(s.format(i0 = i, i1 = inter -1))
        
        #On reset seulement l_mots pour éviter les surcharges
        
        l_mots = [(0, [])]
        
    # A la fin on sauvegarde l'ensemble des données (sauf l_mots) après avoir normé la matrice des vecteurs des mots
    word_vect_matrix = norm_unit(word_vect_matrix)
    save_int()        
            
    
    
def norme(x):
    n = 0
    for xi in x:
        n += xi**2
    return n**(1/2)


def proche(mot, X):
    if not( mot in dm_mots):
        print("not defined")
    else:
        try:            
            Y= word_vect_matrix[dm_mots[mot]]
            return np.dot(X,Y)
        except:
            return None


def distance(mot, X):
    if not( mot in dm_mots):
        print("not defined")
    else:
        u=0
        Y= word_vect_matrix[dm_mots[mot]]
        for i in range(len(X)):
            u+=(X[i]-Y[i])**2
        return u**(0.5)    

def mots_plus_proches(mot, p = 5):
    L = []
    mot_vect = word_vect_matrix[dm_mots[mot]]  
    mot0 = di_mots[0]
    d = abs(proche(mot0 , mot_vect))
    plus_proche = mot0
    L.append((d, plus_proche))
    for mot_text in dm_mots:
        u = proche(mot_text,mot_vect)
        if u== None:
            return L
        else:
            u = abs(u)
        
        n = len(L)
        k = (u,mot_text)
        for i in range(n):
            if L[i][0]<=u :
                k,L[i] = L[i], k
        if n < p:
           L.append(k)
    return L

def mot_plus_proche_vect(mota, motb, motc, p):
    va = word_vect_matrix[dm_mots[mota]]
    vb = word_vect_matrix[dm_mots[motb]]
    vc = word_vect_matrix[dm_mots[motc]]
    
    L = []
    X = (va - vb) + vc
    
    mot0=di_mots[0]
    
    d=abs(proche(mot0,X))
    
    plus_proche=mot0
    
    L.append((d, plus_proche))
    
    for mot in dm_mots:
        u= abs(proche(mot,X))
        k = (u, mot)
        
        if mot == mota or mot == motb or mot == motc:
            continue
        
        n = len(L)
        
        for i in range(n):
            if L[i][0]<=u :
                k,L[i] = L[i], k
        if n < p:            
           L.append(k)
           
    return L
