'''This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details at http://www.gnu.org/licenses/.'''

import numpy as np

'''Crée la liste de toutes les matrices potentielles pour n étudiants, s séances, t systèmes et rest_syst donnant le nombre maximal de système d'un même type pouvant fonctionner en parallèle. Cette fonction n'est pas invoquée dans le main().'''
def matricesPotentielles(n, s, t, rest_syst):
    global L
    L = []    
    def ajoutVal(M, i, j):
        global L
        if i == t-1 and j == s-1:
            L += [M.copy()]
        else:
            next_i = i+(j+1)//s
            next_j = (j+1)%s
            for next_k in range(rest_syst[next_i]+1):
                M[next_i,next_j] = next_k
                if np.sum(M[:,next_j]) <= n//3 and np.sum(M[next_i,:]) <= n//3 and np.sum(M) <= n and n <= np.sum(M)+sum(rest_syst[next_i+1:])*s+rest_syst[next_i]*(s-next_j-1):
                    ajoutVal(np.zeros((t,s), dtype=int)+M, next_i, next_j)    
    M = np.zeros((t,s), dtype=int)
    ajoutVal(M, 0, -1)
    return(L)


