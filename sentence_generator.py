"""
Created on Wed Nov 14 13:57:29 2018

@author: gregoire
"""
import numpy as np 
import copy as copy
from scipy.stats import norm
import os

from pickle import dump,load
 


#on appelle mot un objet de type string
#on appelle phrase une liste de mots



#l'ensembles avec répétition des mots (le texte lu)
l_mots=["\n"]

#nombre de mots connus différents
nb_mots=1



#nombre de livres lus par l'algorithme
limite=300

#l'annuaire est définit de façon recursif:

#un annuaire est un dictionnaire ayant pour clef un entier, et pour valeur
#un couple formé d'un entier et d'un annuaire

#l'annuaire le plus profond est un dictionnaire vide
#on peut voir l'annuaire comme un arbre


#soit p un entier inférieur ou égal a d


#supposons donné i_0,...,i_p  qui sont p+1 indices respectivement des mots m_0,...,m_p
#un annuaire sert a dénombrer les occurrences de la phrase [m_0,...,m_p]


#on note par recurence A_0 l'annuaire le moins profond (içi annuaire) et A_(n+1) l'annuaire tel que 
#A_n[i_n]=(occ_k,A_n+1)

#ainsi, A_p[i_p]=(occ_p, A_(p+1)) si p différent de d
#A_p[i_p]=occ_p si p = d

#occ_p représente alors le nombre d'occurence de la phrase ordronnée [m_0,...,m_p]


annuaire={}



#remarque, si A_n et A_p sont définis commes ci dessus, avec p<n on a len(A_n)<=len(A_p)
#en effet, si la phrase [m_0,...m_p,...,m_n] existe, alors les phrases [m_i,...,m_(i+p)] existent
#pour i dans [0;n-p] donc on a bien plus d'éléments dans A_p





#nombre de couches du programme
d=6

#ditionnaires des mots: "mots"-> indices
dm_mots={}
dm_mots["\n"]=0

#dictionnaire des indices: indices -> "mots"
di_mots={}
di_mots[0]="\n"



#ensemble des caractères concervés lors de la lecture
liaison= [".","!","?",'/','"',"-",",","«","»","…"]
liaison_equ=["'","’"]

#ensemble des mots ignoré lors de la lecture
separateur=[" ", "(",")","\n"]


#lien du fichier a lire
data_base="Data_debug"
#lien du fichier de sauvegarde
save="sauvegarde"




#prend une chaine de caractère et renvoit la liste des mots, séparé par le séparateur
def split_and_keep(chaine):
    L = []
    u= ""
    for i in chaine:
        i=i.lower()
        if i in separateur:
            if u != "":
                L+=[u]
            u=""
        elif i in liaison:
            if u != "":
                L+=[u]
            L+=[i]
            u=""
        elif i in liaison_equ:
            if u != "":
                L+=[u]
            L+=["'"]
            u=""
        else:
            u+=i
    if u != "":
        L+=[u]
    
    return L




#lecture du fichier et remplissage de l_mots


def lecture():
    global nb_mots
    global l_mots
    
    livres_lus=0  
    for dossier, sous_dossiers, fichiers in os.walk(data_base):
        for fichier in fichiers:
            if fichier[-3:]=="txt" and livres_lus<limite:
                livres_lus+=1
                ##if livres_lus%50==0:
                    ##print(livres_lus)
                lien=os.path.join(dossier, fichier)
                ##print(lien)
                with open(lien,'r') as line:
                    for x in line.readlines():
                        for y in split_and_keep(x):
                            
                            #si le mot n'a jamais été rencontré, il faut l'ajouter aux ictionnaires
                            if not y in dm_mots:
                                dm_mots[y]=nb_mots
                                di_mots[nb_mots]=y
                                nb_mots+=1
                                
                                
                            l_mots+=[y]
            
           
#création de l'annuaire, selon la méthode expliquée
   

         
        
            
def analyse():
    lecture()
    
    global annuaire
        
        #on garde en mémoire l'accès aux d derniers annuaires afin de tous les actualiser
    #lorsqu'un nouveau mot est lu
    #l_annuaire[i]=[occi',Ann]
    l_annuaire=[]            
                
                
       #on remplit la liste mémoire tout en remplissant l'annuaire des d premiers mots
    for i in range(d):
            
        mot=l_mots[i]
            
            #l_annuaire=[A0,...,Ai]
            
        if not mot in annuaire:
            annuaire[mot]=[0,{}] #On ajoute les mots dans l'annuaire
        annuaire[mot][0]+=1
        l_annuaire.append(annuaire[mot])
          
            
            
        for ind_couple in range(i):
            couple=l_annuaire[ind_couple] #On initialise les annuaires précédents
            if not mot in couple[1]:
                couple[1][mot]=[0,{}]
            l_annuaire[ind_couple]=couple[1][mot] #On descend d'une profondeur supplémentaire : copie en alias
            l_annuaire[ind_couple][0]+=1
                
                
        #içi, les i annuaires de l_anuaires sont actualisée
    #a la fin de la boucle, on a une liste a d élements, qui correspondent a nos listes initialisées
    
    
    #on traite le cas général           
    for k in range(d,len(l_mots)):
        mot=l_mots[k]
            
        #On détruit la dernière instance d'annuaire, car on ne va pas plus loin que d
        l_annuaire.pop(0)
        
        
        
        #on actualise les annuaires
        for ind_couple in range(d-1):
            couple=l_annuaire[ind_couple]
            if not mot in couple[1]:
                couple[1][mot]=[0,{}]
            l_annuaire[ind_couple]=couple[1][mot]
            l_annuaire[ind_couple][0]+=1
                
                
        #on ajoute le nouvel annuaire
        if not mot in annuaire:
            annuaire[mot]=[0,{}]
        annuaire[mot][0]+=1
        l_annuaire.append(annuaire[mot])
 

#sauvegarde
def sauvegarde():
    
    dfg=open(save,'wb')
    dump(annuaire,dfg)
    dfg.close()

def ouverture():
    global annuaire
    aze=open(save,'rb')
    annuaire=load(aze)
    aze.close()

#renvoit la liste des mots qui ont pour suivant le mot mot
def precedant(mot):
    L=[]
    indice=dm_mots[mot]
    for ind in di_mots:
        if indice in annuaire[ind][1]:
            L+=[di_mots[ind]]
    return L
       
            
           
 


def aleatoire_d(liste):
    u=annuaire
    for ind in liste:
        u=u[ind][1]
    
    
    #crée une liste de couples (mot k ,[occurence de k après i et j, dictionnaire])
    ltot=list(u.items())
    
    
    locc=np.array([])
    for couple in ltot:
        locc=np.append(locc, couple[1][0])
    
    #on norme ce vecteur
    somme= np.sum(locc)
    l_norme= locc/somme
    
    #renvoit un indice k d'un mot,  pondéré par les occurences des mots j après le mot ii
    k=np.random.choice(len(ltot),1,p=list(l_norme))[0]
    return ltot[k][0]

        
           


# génere une phrase aléatoire en regardant d mots en arrières
def generer(d):
    L=[]
    #on a donc besoin de garder en mémoire les d derniers mots
    mem=[]
    taille_mem=0
    
    indice=dm_mots["."]
    mot="."
    
    #on cherche le premier mot qui n'est pas "."
    while mot == ".":
        indice=aleatoire_d([indice])
        mot=di_mots[indice]
        
        
    taille_mem=1
    mem+=[indice]
    
    
    L+=[mot]
    
    while mot != ".":
        indice= aleatoire_d(mem)
        mot=di_mots[indice]
        
        L+=[mot]
     
        if taille_mem<d:
            taille_mem+=1
        else:
            mem.pop(0)
        mem+=[indice]  
        
    return L


#Calcule le poid d'un mots
#Le poids est içi décidé par sa fréquence d'apparition
def poid(i):
    nbMotsTot=len(l_mots)
    if dm_mots[i] in annuaire:
        nbAppMot=annuaire[dm_mots[i]][0]
        return nbAppMot/nbMotsTot
    else: 
        return 0

#donne le tableau des occurences des mots de taille d dans l'annuaire ann
def aux(ann,d):
    #on va écrire ce programme de façon récursive
    if d == 1:
        L=[]
        for mot in ann:
            L.append(annuaire[mot][0])
    else:
        L=[]
        for mot in ann:
            L+=aux(ann[mot][1],d-1)
    return L

#donne le tableau des occurences des mots de taille d (application du programme précédant)
def liste_occ(d):
    return aux(annuaire,d)





#Calcule le poid d'une phrase
#Le poids est içi décidé par sa fréquence d'apparition
def poid_phrase(liste):
    occ_phrase=0
    
    
    d=len(liste)
    
    u=annuaire
    
    for i in range(d-1):
        ind=liste[i]
        if dm_mots[ind] in u:
            u=u[dm_mots[ind]][1]
        else:
            occ_phrase=-1
            break
     
        
    ind=liste[d-1]
    if dm_mots[ind] in u:
        u=u[dm_mots[ind]]
    else:
        occ_phrase=-1
    
    if occ_phrase != -1: 
        occ_phrase = u[0]
        ntot=np.sum(liste_occ(d))
        return occ_phrase/ntot
    else:
        return 0


#On définit aussi la probabilité d'apparition comme 
#P(phrase)=freq(phrase)^(3/4) / (   somme freq(phrases)^(3/4)  )
def proba(liste):
    d=len(liste)
    
    freq=poid_phrase(liste)
    liste_occs=liste_occ(d)
    denominateur=0
    for j in liste_occs:
        denominateur+=j**(3/4)
    return freq**(3/4)/denominateur


#Probabilité améliorée qui ne se base que sur l'évaluation du dernier mot
#le calcul reste le même, c'est l'échantillon considéré qui change
def proba_2(liste):
    
    #on le fera de façon récursive, dans le cas où la phrase n'est pas dans l'annuaire
    #On en réduit progressivement la taille
    d=len(liste)
    #cas de base
    if d==1:
        mot= liste[0]
        occ_mot=0
        ind=dm_mots[mot]
        
        if ind in annuaire:
            occ_mot= annuaire[ind][0]
        else:
            return 0
        
        
        liste_occs=liste_occ(1)
        denominateur=0
        for j in liste_occs:
            denominateur+=j**(3/4)
        return (occ_mot**(3/4))/denominateur
        
        
        
    #cas général
    else:    
        
        u=annuaire
        
        #On va chercher l'annuaire le plus profond
        for i in range(d-1):
            mot=liste[i]
            if mot in dm_mots:
                ind=dm_mots[mot]
            else:
                return 0
            if ind in u:
                u=u[ind][1]
            else:
                #si on ne trouve pas la phrase, on enlève le premier mot
                #et on recommence
           ##     liste.pop(0)
             ##   return proba_2(liste)
             
                 return 0
             
                 
        mot= liste[d-1]
        if not mot in dm_mots:
            return 0
        else:    
            ind= dm_mots[mot]
        if not(ind in u):
            
         ##   liste.pop(0)
        ##    return proba_2(liste)
        
            return 0
        else:
            u=u[ind]
            occ=u[0]
            liste_occs=aux(u[1],1)
            
            
            denominateur=0
            for j in liste_occs:
                denominateur+=j**(3/4)
            return (occ**(3/4))/denominateur
        
        
#Renvoit une liste constituée des différentes probabilitées pour chaque
#sous-phrase de taille d
def l_proba(phrase,d):
    n=len(phrase)
    if n<=d:
        return [proba_2(phrase)]
    else:
        L=[]
        for i in range(n-d):
            L.append (proba_2(phrase[i:i+d]))
        return L