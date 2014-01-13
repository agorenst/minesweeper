import sys
import socket
import pygame

pygame.init()

UNKNOWN = -2
MINE = -1

class Grid(object):
    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.m = m
        self.g = [[UNKNOWN for i in range(x)] for j in range(y)]
    def __getitem__(p):
        x = p[0]
        y = p[1]
        return self[x,y]
    def __getitem__(x,y):
        return self.g[y][x]
    def drawBasic():
        for i in range(self.x):
            for j in range(self.y):
                square = (i*squarelen, j*squarelen, squarelen, squarelen)
                pygame.draw.rect(window, (100, 0, 100), square, 0)


X = 15
Y = 10
squarelen = 20
grid = [[0 for i in range(X)] for j in range(Y)]

window = pygame.display.set_mode((X*squarelen,Y*squarelen))

t = socket.create_connection(("localhost", 8080))

#for i in range(y):
#    for j in range(x):
#        print '['+str(grid[i][j])+']',
#    print

def inBounds(x,y):
    return 0 <= x and x < X and 0 <= y and y < Y

minechars = [pygame.font.SysFont(None,squarelen).render(str(i), 1, (0,100,100)) for i in range(10)]
minepic = pygame.font.SysFont(None,squarelen).render('M', 1, (0,100,100))

def drawBasicGrid(): 
    for i in range(X):
        for j in range(Y):
            square = (i*squarelen, j*squarelen, squarelen, squarelen)
            if grid[j][i] == 0:
                pygame.draw.rect(window, (100,0,100), square, 0)
            else:
                pygame.draw.rect(window, (0,0,0), square, 0)

def drawGridOutline():
    # draw an outline around every box
    for i in range(X):
        for j in range(Y):
            square = (i*squarelen, j*squarelen, squarelen, squarelen)
            pygame.draw.rect(window, (0,0,0), square, 5)

#def drawMineCount():
#    for i in range(x):
#        for j in range(y):
#            t.send(str(i)+" "+str(j)+" Q")
#            res = t.recv(4096)
##            if res == '-1':
##                grid[j][i] = 1
#            minecount = int(res)
#            if minecount >= 0 and minecount < 10:
#                rect = minechars[minecount].get_rect()
#                rect.center = ((i+0.5)*squarelen, (j+0.5)*squarelen)
#                window.blit(minechars[minecount], rect)


def drawMineCount(i, j):
    n = kgrid[j][i]
    rect = minechars[n].get_rect()
    rect.center = ((i+0.5)*squarelen, (j+0.5)*squarelen)
    window.blit(minechars[n], rect)

def drawMine(i,j):
    n = kgrid[j][i]
    # n should be -1
    rect = minepic.get_rect()
    rect.center = ((i+0.5)*squarelen, (j+0.5)*squarelen)
    window.blit(minepic, rect)

def drawKGrid():
    for i in range(X):
        for j in range(Y):
            state = kgrid[j][i]
            if state >= 0:
                drawMineCount(i,j)
            if state == -1:
                drawMine(i,j)



# just saving the raw data from the server
qgrid = [[-2 for i in range(X)] for j in range(Y)]
# combining qgrid with some of our own reasoning
kgrid = [[-2 for i in range(X)] for j in range(Y)]
# essentially the cells that we have already queried,
# but have unknown (interesting) neighbors
toprocess = []
# the cells we want to query from the server (ideally,
# those we have determined are safe)
toquery = [(8,1),(6,4),(7,4),(8,4)]

def queryServer(p):
    t.send(str(p[0])+" "+str(p[1])+" Q")
    res = t.recv(4096)
    # eventually we'll have to be smarter about this
    print 'updating', p, 'with', res
    qgrid[p[1]][p[0]] = int(res)
    kgrid[p[1]][p[0]] = int(res)

def neighborList(p):
    x = p[0]
    y = p[1]
    for i in range(-1,2):
        for j in range(-1,2):
            if i != 0 or j != 0:
                xprime = x + i
                yprime = y + j
                if inBounds(xprime, yprime):
                    yield (xprime, yprime)


def runAI(G, P, Q):
    print "Starting runAI"
    print P
    print Q
    nP = set([])
    for p in P:
        print "Processing for", p
        minecount = G[p[1]][p[0]]
        print "Minecount:", minecount
        if minecount == -2:
            continue
        unknownneighbors = []
        mineneighbors = []
        for n in neighborList(p):
            print "neighbor:", n
            if kgrid[n[1]][n[0]] == -2:
                unknownneighbors += [n]
            elif kgrid[n[1]][n[0]] == -1:
                mineneighbors += [n]

        print "We're doing this for", p
        print minecount, unknownneighbors, mineneighbors

        if len(unknownneighbors) == 0:
            continue

        if minecount - len(mineneighbors) == 0:
            Q += unknownneighbors
            continue

        if minecount - len(mineneighbors) == len(unknownneighbors):
            for n in unknownneighbors:
                kgrid[n[1]][n[0]] = -1
            continue

        nP.add(p)

    for q in Q:
        queryServer(q)
        nP.add(q)
    Q = []
    return G, nP, Q


while True:
    drawBasicGrid()
    drawGridOutline()
    #drawMineCount()
    drawKGrid()
    stall = raw_input("hit enter to continue")
    newstate = runAI(kgrid,toprocess,toquery)
    toprocess = newstate[1]
    toquery = newstate[2]
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            t.close()
            sys.exit(0)
#        else:
#            print event

