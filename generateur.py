'''This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details at http://www.gnu.org/licenses/.'''

import numpy as np
import itertools as it
import pycosat as sat
from encodages import contrEgal, contrInf

def main():
    '''On définit le nombre d'étudiants, les noms et les restrictions liées aux systèmes, et la matrice P de planning des systèmes par séances.'''
    n = 24
    
    type_syst = ["DMX", "WIFIBOT", "DAMALISK", "SIMRAD"]
    rest_syst = [2, 2, 1, 1]
    
    P = np.array([[2, 2, 2, 2],
                  [2, 2, 2, 2],
                  [1, 1, 1, 1],
                  [1, 1, 1, 1]])
    
    '''On vérifie si la matrice satisfait les conditions nécessaires. Ceci n'est pas nécessaire si l'une des contraintes assouplies est choisie.'''
    assert(checkPotentielle(n, P, rest_syst))
    
    '''On construit les partitions T et S et on génère les contraintes correspondantes.'''
    T, S = partitions(n, P)
    C = contraintes(n,T,S)
    
    prop_limit = 1_000_000_000
    solution = sat.solve(C, prop_limit=prop_limit)
    
    '''Si une solution a été trouvée, on l'imprime sous la forme d'un fichier csv, sinon on précise si le solutionneur a abouti ou pas.'''
    if solution == "UNSAT":
        print("Il n'y a pas de solution au problème donné.")
    elif solution == "UNKNOWN":
        print("Le solutionneur n'a pas abouti dans la limite de propagation : " + str(prop_limit))
    else:
        tab_sol = tableau(solution, n)
        solutionCSV(tab_sol, type_syst, T, S)
    return C, solution

'''Permet de définir T et S en fonction de P.'''
def partitions(n, P):
    T = [[] for k in range(P.shape[0])]
    S = [[] for k in range(P.shape[1])]    
    k = 0
    lt = 0
    ls = 0
    while k < n:
        T[lt]+=list(range(k, k + P[lt, ls]))
        S[ls]+=list(range(k, k + P[lt, ls]))
        k+=P[lt, ls]
        if lt == (P.shape[0] - 1):
            lt = 0
            ls+=1
        else:
            lt+=1
    return T, S

'''Définit les contraintes pour le solveur.'''
def contraintes(n, T, S):
    X = np.array(np.array_split(range(1, n**2+1), n))
    Y = np.array(np.array_split(range(n**2+1, 2*n**2+1), n))
    
    contr, fin = [], 2*n**2
    
    '''Contrainte 1: Chaque étudiant participe à exactement 3 équipes.'''
    for i in range(n):
        contr, fin = contrEgal(X[i], 3, contr, fin)

    '''Contrainte 2: Il y a exactement 3 étudiants par équipe.'''
    for j in range(n):
        contr, fin = contrEgal(X[:,j], 3, contr, fin)

    '''Contrainte 3: Un étudiant ne peut pas faire partie de deux équipes au cours d'une même séance.'''
    for l in range(len(S)):
        for i in range(n):
            contr, fin = contrInf(X[i,S[l]], 1, contr, fin)

    '''Contrainte 4: Un étudiant ne peut pas intervenir sur deux systèmes du même type. Pour utiliser la contrainte assouplie 4' remplacez 1 par 2.'''
    for l in range(len(T)):
        for i in range(n):
            contr, fin = contrInf(X[i,T[l]], 1, contr, fin)
        
    '''Contrainte 5: Deux étudiants ne peuvent pas se retrouver deux fois ensemble en équipe.'''
    for i in it.combinations(range(n), 2):
        for j in it.combinations(range(n), 2):
            contr += [[int(-X[i[x[0]], j[x[1]]]) for x in it.product(range(2), range(2))]]
    '''Contrainte 5': Version assouplie de la contrainte 5.'''
    '''for i in it.combinations(range(n), 2):
        for j in it.combinations(range(n), 3):
            contr+=[[int(-X[i[x[0]], j[x[1]]]) for x in it.product(range(2), range(3))]]
    for i in it.combinations(range(n), 3):
        for j in it.combinations(range(n), 2):
            contr+=[[int(-X[i[x[0]], j[x[1]]]) for x in it.product(range(3), range(2))]]'''
    
    '''Contrainte 6: Toute équipe possède exactement un chef d'équipe.'''
    for j in range(n):
        contr, fin = contrEgal(Y[:,j], 1, contr, fin)
    
    '''Contrainte 7: Tout étudiant doit être chef d'équipe exactement une fois.'''
    for i in range(n):
        for j in range(n):
            contr += [[int(X[i, j]), -int(Y[i, j])]]
    for i in range(n):
        contr, fin = contrEgal(Y[i], 1, contr, fin)
    
    return contr

'''Permet de mettre une solution sous une forme plus lisible de tableau en représentant les techniciens par 1 et les chefs d'équipe par 2.'''
def tableau(solution, n):
    tab_sol = np.zeros((n,n), dtype=int)
    for k in range(n**2):
        if solution[k] > 0:
            tab_sol[k//n, k%n]+=1
    for k in range(n**2, 2*n**2):
        if solution[k] > 0:
            tab_sol[k//n - n, k%n]+=1
    return tab_sol

'''Crée et remplit un fichier csv qui donne le planning des étudiants. Pour lire le csv dans le tableur, il faudra éventuellement préciser l'encodage.'''
def solutionCSV(tab_sol, type_syst, T, S):
    
    def code_syst(j):
        for t in range(len(T)):
            for k in range(len(T[t])):
                if T[t][k] == j:
                    return type_syst[t] + " #" + str(k+1)
    
    file = open('Planning_étudiants.csv','w')
    for i in range(tab_sol.shape[0]):
        ligne = "Etudiants #" + str(i+1) + ";"
        for s in range(len(S)):
            seance_s = ""
            for j in S[s]:
                if tab_sol[i,j] == 2:
                    seance_s+="Chef d'équipe pour "+code_syst(j)
                elif tab_sol[i,j] == 1:
                    seance_s+="Technicien pour "+code_syst(j)
            ligne+=seance_s + ";"
        file.write(ligne[:-1] + "\n")
    file.close()

'''Permet de vérifier si la matrice vérifie a priori une série de contraintes nécessaires à l'existence d'une solution pour le problème SAT.'''
def checkPotentielle(n, P, rest_syst):
    t = P.shape[0]
    s = P.shape[1]
    return np.sum(P) == n and (np.sum(P, 0) <= (n//3) * np.ones(s, dtype=int)).all() and (np.sum(P, 1) <= (n//3) * np.ones(t, dtype=int)).all() and (P <= np.array([rest_syst for x in range(s)]).T).all()

main()
