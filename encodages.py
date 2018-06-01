'''This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details at http://www.gnu.org/licenses/.'''

import numpy as np
import itertools as it

'''Ce code permet de déterminer et de renvoyer l'encodage le mieux adapté pour les contraintes de cardinalité <=K(X) et =K(X) entre l'encodage naïf, l'encodage séquentiel de Sinz et l'encodage séquentiel bidirectionnel de Delacroix [T. Delacroix, Choisir un encodage CNF de contraintes de cardinalité performant pour SAT, CNIA 2018]. Le critère utilisé est le nombre total de littéraux.'''

'''Renvoie les contraintes et l'indice de la dernière variable en choisissant l'encodage le mieux adapté pour <=K(X)'''
def contrInf(X, K, C, end):
    n = len(X)
    contr = []
    if n <= 5 or K == n-1 or (n <= 27 and K == n-2):
        contr += contrInfNaive(X, K)
    elif 3*K <= 2*n:
        contr += contrInfSinz(X, K, end + 1)
        end += (n-1) * K
    else:
        contr += contrSupDlx(-X, n-K, end + 1)
        end += n * (n-K+1)
    return C+contr, end

'''Renvoie les contraintes et l'indice de la dernière variable en choisissant l'encodage le mieux adapté pour =K(X)'''
def contrEgal(X, K, C, end):
    n = len(X)
    contr = []
    if n <= 5 or (n == 6 and (K == 3 or K == 5) ):
        contr += contrSupNaive(X, K)
        contr += contrInfNaive(X, K)
    elif K <= 1 or K <= 2 or (K == 3 and n == 7):
        contr += contrInfNaive(X, K)
        contr += contrInfSinz(-X, n-K, end + 1)
        end += (n - 1) * (n-K)
    elif K == n-1 or K == n-2 or (K == 4 and n == 7):
        contr += contrInfNaive(-X, n-K)
        contr += contrInfSinz(X, K, end + 1)
        end += (n - 1) * K
    else:
        contr += contrEgalDlx(X, K, end + 1)
        end += n * (K+1)
    return C+contr, end

'''Encodage naïf de <=K(X)'''
def contrInfNaive(X, K):
    n = len(X)
    C = []
    for i in it.combinations(range(n), K+1):
        C += [ [int(-X[i[x]]) for x in range(K+1)] ]
    return C

'''Encodage de <=K(X) par Sinz, ajoute (n-1)*K variables'''
def contrInfSinz(X, K, start):
    n = len(X)
    S = np.array(np.array_split(range(start, (n-1)*K+start),n-1))
    C = []
    i = 0
    j = 0
    C += [ [int(-X[i]), int(S[i,j])] ]
    for j in range(1,K):
        C += [ [int(-S[i,j])] ]
    for i in range(1,n-1):
        j = 0
        C += [ [int(-X[i]), int(S[i,j])] ]
        C += [ [int(-S[i-1,j]), int(S[i,j])] ]
        for j in range(1,K):
            C += [ [int(-X[i]), int(-S[i-1,j-1]), int(S[i,j])] ]
            C += [ [int(-S[i-1,j]), int(S[i,j])] ]
        j = K
        C += [ [int(-X[i]), int(-S[i-1,j-1])] ]
    i = n-1
    C += [ [int(-X[i]), int(-S[i-1,j-1])] ]
    return C

'''Encodage de <=K(X) par Delacroix, ajoute n*(K+1) variables'''
def contrInfDlx(X, K, start):
    n = len(X)
    S = np.array(np.array_split(range(start, n*(K+1)+start),n))
    C = []
    i = 0
    j = 0
    C += [ [int(-X[i]),int(S[i,j])], [int(X[i]),int(-S[i,j])] ]
    for i in range(1,n):
        j = 0
        C += [ [int(-X[i]),int(S[i,j])] ]
        C += [ [int(-S[i-1,j]), int(S[i,j])] ]
        C += [ [int(X[i]), int(-S[i,j]), int(S[i-1,j])] ]
        for j in range(1,K+1):
            C += [ [int(-S[i-1,j]), int(S[i,j])] ]
            C += [ [int(X[i]), int(-S[i,j]), int(S[i-1,j])] ]
            C += [ [int(-S[i,j]), int(S[i-1,j-1])] ]
            C += [ [int(-X[i]), int(-S[i-1,j-1]), int(S[i,j])] ]
    for j in range(K):
        C += [ [int(-S[j,j+1])] ]
    C += [ [-int(S[n-1,K])] ]
    return C

'''Encodage de >=K(X) par Delacroix, ajoute n*(K+1) variables'''
def contrSupDlx(X, K, start):
    n = len(X)
    S = np.array(np.array_split(range(start, n*(K+1)+start),n))
    C = []
    i = 0
    j = 0
    C += [ [int(-X[i]),int(S[i,j])], [int(X[i]),int(-S[i,j])] ]
    for i in range(1,n):
        j = 0
        C += [ [int(-X[i]),int(S[i,j])] ]
        C += [ [int(-S[i-1,j]), int(S[i,j])] ]
        C += [ [int(X[i]), int(-S[i,j]), int(S[i-1,j])] ]
        for j in range(1,K+1):
            C += [ [int(-S[i-1,j]), int(S[i,j])] ]
            C += [ [int(X[i]), int(-S[i,j]), int(S[i-1,j])] ]
            C += [ [int(-S[i,j]), int(S[i-1,j-1])] ]
            C += [ [int(-X[i]), int(-S[i-1,j-1]), int(S[i,j])] ]
    for j in range(K):
        C += [ [int(-S[j,j+1])] ]
    C += [ [int(S[n-1,K-1])] ]
    return C

'''Encodage de =K(X) par Delacroix, ajoute n*(K+1) variables'''
def contrEgalDlx(X, K, start):
    n = len(X)
    S = np.array(np.array_split(range(start, n*(K+1)+start),n))
    C = []
    i = 0
    j = 0
    C += [ [int(-X[i]),int(S[i,j])], [int(X[i]),int(-S[i,j])] ]
    for i in range(1,n):
        j = 0
        C += [ [int(-X[i]),int(S[i,j])] ]
        C += [ [int(-S[i-1,j]), int(S[i,j])] ]
        C += [ [int(X[i]), int(-S[i,j]), int(S[i-1,j])] ]
        for j in range(1,K+1):
            C += [ [int(-S[i-1,j]), int(S[i,j])] ]
            C += [ [int(X[i]), int(-S[i,j]), int(S[i-1,j])] ]
            C += [ [int(-S[i,j]), int(S[i-1,j-1])] ]
            C += [ [int(-X[i]), int(-S[i-1,j-1]), int(S[i,j])] ]
    for j in range(K):
        C += [ [int(-S[j,j+1])] ]
    C += [ [-int(S[n-1,K])] ]
    C += [ [int(S[n-1,K-1])] ]
    return C
