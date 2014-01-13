import sys
import socket
import pygame

# creating and initializing graphics assets.

X = 15
Y = 10

pygame.init()
squarelen = 20
minechars = [pygame.font.SysFont(None,squarelen).render(str(i), 1, (0,100,100)) for i in range(10)]
minepic = pygame.font.SysFont(None,squarelen).render('M', 1, (0,100,100))

# handy global constants

UNKNOWN = -2
MINE = -1

class Grid(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = [[UNKNOWN for i in range(x)] for j in range(y)]
    def __getitem__(self,p):
        x = p[0]
        y = p[1]
        return self.g[y][x]
    def __setitem__(self,p,v):
        self.g[p[1]][p[0]] = v
    def drawBasic(self):

        # maybe change background based off of square state.
        for i in range(self.x):
            for j in range(self.y):
                square = (i*squarelen, j*squarelen, squarelen, squarelen)
                pygame.draw.rect(window, (100, 0, 100), square, 0)

        # draw a black outline around each square.
        for i in range(self.x):
            for j in range(self.y):
                square = (i*squarelen, j*squarelen, squarelen, squarelen)
                pygame.draw.rect(window, (0,0,0), square, 5)

    def inBounds(self,x,y):
        return 0 <= x and x < self.x and 0 <= y and y < self.y

    def drawMine(self,x,y):
        rect = minepic.get_rect()
        rect.center = ((x+0.5)*squarelen, (y+0.5)*squarelen)
        window.blit(minepic, rect)
    def drawNum(self,x,y,n):
        rect = minechars[n].get_rect()
        rect.center = ((x+0.5)*squarelen, (y+0.5)*squarelen)
        window.blit(minechars[n], rect)

    def draw(self):
        self.drawBasic()
        for i in range(self.x):
            for j in range(self.y):
                state = self.g[j][i]
                if state >= 0:
                    self.drawNum(i,j,state)
                if state == -1:
                    self.drawMine(i,j)

    def neighborList(self,p):
        x = p[0]
        y = p[1]
        for i in range(-1,2):
            for j in range(-1,2):
                if i != 0 or j != 0:
                    xprime = x + i
                    yprime = y + j
                    if self.inBounds(xprime, yprime):
                        yield (xprime, yprime)

    def unknownNeighbors(self, p):
        for n in self.neighborList(p):
            if self[n] == UNKNOWN:
                yield n

    def mineNeighbors(self, p):
        for n in self.neighborList(p):
            if self[n] == MINE:
                yield n
        




# these are the two clients we interact with.
t = socket.create_connection(("localhost", 8080))
window = pygame.display.set_mode((X*squarelen,Y*squarelen))


def queryServer(G,p):
    t.send(str(p[0])+" "+str(p[1])+" Q")
    res = t.recv(4096)
    # eventually we'll have to be smarter about this
    G[p] = int(res)


def runAI(G, P, Q):
    # we can't remove elements as we iterate,
    # so instead we ''re-add'' all elements
    # that still need processing
    nP = set([])
    for p in P:
        minecount = G[p]
        if minecount == UNKNOWN:
            continue
        unknownneighbors = set(list(G.unknownNeighbors(p)))
        mineneighbors = set(list(G.mineNeighbors(p)))

        if len(unknownneighbors) == 0:
            continue

        if minecount - len(mineneighbors) == 0:
            Q.update(unknownneighbors)
            continue

        if minecount - len(mineneighbors) == len(unknownneighbors):
            for n in unknownneighbors:
                G[n] = -1
            continue

        nP.add(p)

    for q in Q:
        queryServer(G,q)
        nP.add(q)
    Q = set([])
    return G, nP, Q


def main():
    # this is the main grid we use
    G = Grid(X, Y)

    # these are the cells we've already queried,
    # but may have interesting neighbors
    P = set([])
    # the cells we want to query from the server (ideally,
    # those we have determined are safe)
    Q = set([(8,1),(6,4),(7,4),(8,4)])
    while True:
        G.draw()
        stall = raw_input("hit enter to continue")
        newstate = runAI(G,P,Q)
        G = newstate[0]
        P = newstate[1]
        Q = newstate[2]
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                t.close()
                sys.exit(0)

main()
