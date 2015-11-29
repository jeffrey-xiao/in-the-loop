'''
Created on Nov 28, 2015

@author: Jeffrey
'''
prev = []
v = []
def getMatching (N, M, adj):
    global prev, v
    prev = [-1]*M
    for i in range(N):
        v = [False]*M
        match(i, N, M, adj)
    res = []
    for i in prev:
        if i != -1:
            res += [i]
    return res
def match (i, N, M, adj):
    for j in range(M):
        if adj[i][j] and not v[j]:
            v[j] = True
            if prev[j] == -1 or match(prev[j], N, M, adj):
                prev[j] = i
                return
    return

print getMatching(3, 4, [[False, True, False, False],
                   [False, True, False, True],
                   [False, False, False, True]])