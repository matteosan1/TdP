import random 
import sys
import pygame
from PyQt4.QtNetwork import *

class Cavallo:
    def __init__(self, n):
        self.nome = n
        self.scatto = 1
        self.vel_max = int(random.uniform(40, 60))
        self.resistenza = int(random.uniform(50,100))
        self.precisione = int(random.uniform(0,2))
        self.allenamento = 1

class Point:
    def __init__(self):
        self.coord = (0,0)
        self.angle = 0
        self.val = 0
        self.pos = 0
        self.leafs = (0,0,0)
    
    def set_point(self, p):
        self.coord = (int(p[0]), int(p[1]))
        self.angle = float(p[2])
        self.val = int(p[3])
        self.pos = int(p[4])
        self.leafs = (int(p[5]), int(p[6]), int(p[7]))

class Barbero():
    def __init__(self, n, i):
        self.cavallo = Cavallo(n)
        self.pos = Point()
        self.t = 0
        self.giro = 0
        self.traiettoria = []
        self.velocita = 0
        self.riserva = self.cavallo.resistenza*self.cavallo.allenamento
        self.scosso = True
        self.indice = i

    def setPosizione(self, p):
        self.pos = p

    def accelera(self):
        self.velocita += self.cavallo.scatto 
        self.riserva -= 5 # FIXME

    def decelera(self):
        self.velocita -= self.cavallo.scatto 

def ordinaBarberiFunc(b1, b2):
    if (b1.giro < b2.giro):
        return 1
    elif (b1.giro > b2.giro):
        return -1
    else:
        if ((b1.pos.pos <= b2.pos.pos) or
            ((b1.pos.pos == b2.pos.pos) and (b1.pos.val > b2.pos.val))):
            return 1
        return -1

def ordinaPathsFunc(p1, p2):
    if (p1[0] == p2[0]):
        return (abs(p1[1]) < abs(p2[1]))
    else:
        return (p1[0] < p2[0])

class Engine():
    def __init__(self, n):
        self.barberi = [Barbero(n[i], i) for i in xrange(len(n))]    
        self.piazza = []
        self.ordine = []

        self.sockets = []

    def loadMap(self):
        file = open("mappa_piazza2.csv")
        lines = file.readlines()
        for line in lines:
            numbers = (line.split("\n")[0]).split(",")
            p = Point()
            p.set_point(numbers)
            self.piazza.append(p)
        
    def mossa(self):
        for i, b in enumerate(self.barberi):
            b.setPosizione(self.piazza[164+i])
            b.accelera()
        
    def getPositions(self):
        posList = []
        for b in self.barberi:
            posList.append([b.indice, b.pos_int.coord, b.pos.coord, b.velocita])
        
        return posList
  
    def dist(self, p, b2):
        return (((p.pos-b2.pos.pos), abs(p.val)-abs(b2.pos.val)))

    def ordinaBarberi(self):
        self.barberi = sorted(self.barberi, cmp=ordinaBarberiFunc)

    def handicap(self, leaf, precisione):
        if (leaf != -1):
            h = abs(self.piazza[leaf].val + precisione)

            # evita collisioni con altri cavalli
            for y in xrange(len(self.barberi)):
                dx = self.dist(self.piazza[leaf], self.barberi[y])[1] 
                dy = self.dist(self.piazza[leaf], self.barberi[y])[0]     

                if ((dy > 2) or (dx > 0) or (dx < -2)):
                    h = h+0
                elif (dy == 1):
                    h = h+2
                elif (dy == 0 and dx == -2):
                    h = h+4
                elif (dy == 0 and dx == -1):
                    h =h+8
                elif (dy == 0 and dx == 0):
                    h=h+9999
                else:
                    h= h+2
            #else:
            #    return 9999
            return h

    def isVicoloCieco(self, leaf, v, direzione):
        for i in xrange(v):
            new_leaf = self.piazza[leaf].leafs[1]
            if (new_leaf == -1):
                if (self.piazza[leaf].leafs[direzione] == -1):
                    return v-i
                else:
                    new_leaf = self.piazza[leaf].leafs[direzione]
    
        return 0
    
    def fineCorsa(self):
        sys.exit(1)

    def move(self):
        for z,b  in enumerate(self.barberi):
            turns = [-1, 0, 1]
            paths = [[self.handicap(l, b.cavallo.precisione), turns[j], l] for j,l in enumerate(b.pos.leafs) if (l != -1)]
            #if (z == 0):
            #    print "start"
            #    print paths

            iterations = int(b.velocita*1.25)
        
            for iteration in xrange(iterations):
                temp_paths = []
                #print len(paths)
                for path in paths:
                    current_val = self.piazza[path[-1]].val
                    #print path[-1]
                    #print self.piazza[path[-1]].leafs
                    for leaf in self.piazza[path[-1]].leafs:
                        if (leaf != -1):
                            handy = self.handicap(leaf, b.cavallo.precisione)
                            if (handy >= 9999):
                                #print "occupata"
                                continue

                            # CONTROLLARE NELLA SPIANATA DOVE SONO TUTTI 0
                            deltaX = self.piazza[leaf].val - current_val
                            if (deltaX * path[1] < 0):
                                #print "ricurvi", deltaX, path[1]
                                continue

                            if (deltaX != 0):
                                path[1] = deltaX
                                handy += self.isVicoloCieco(leaf, (iterations-iteration), path[1]+1)
                            #print [path[0]+handy] + [path[1]] + path[2:]+[leaf]
                            if (self.piazza[leaf].pos == 340):
                                b.giro += 1
                                if (b.giro > 2):
                                    # da migliorare
                                    self.fineCorsa()
                            temp_paths.append([path[0]+handy] + [path[1]] + path[2:]+[leaf])

                # cleaning
                #if (z == 0):
                #    print temp_paths
                temp_paths = sorted(temp_paths, cmp=ordinaPathsFunc)
                #if (z == 0):
                #    if (len(temp_paths) == 0):
                #        sys.exit()
                #    print temp_paths
                if (len(temp_paths) != 0):
                    #print "temp_paths", temp_paths
                    paths = temp_paths[0:3]
                else:
                    #print "FRENATA !!!"
                    if (iteration < b.velocita):
                        b.velocita = iteration-1
                        break
                    # INFORUNIO CAVALLO !!!
                #print paths
                #print len(paths), b.pos.val, b.pos.pos

            # velocita
            if (b.scosso):
                #print paths[0]
                #print b.velocita, len(paths[0]), int(b.velocita)+2, int(int(b.velocita)/2)+2
                if (len(paths) > 0):
                    dist = 0.
                    indice = 2
                    #print iterations
                    #print len(paths[0]), indice, b.t, b.velocita, len(paths[0])
                    for i in xrange(int(b.velocita)):
                        dist += (1-max(0,self.piazza[paths[0][indice]].val)*.2)
                        #print dist, self.piazza[paths[0][indice]].val
                        indice = int(dist) + 2
                        b.t = dist%1.0
                    #print len(paths[0]), indice, b.t

                    b.pos = self.piazza[paths[0][indice]]
                    b.traiettoria = [b.indice]
                    # DA MIGLIORARE
                    for n, i in enumerate(paths[0][2:indice]):
                        b.traiettoria += [round(float(n+1)/b.velocita, 3), self.piazza[i].coord]
                    #b.traiettoria = paths[0][2:indice]

                if ((b.pos.pos > 150 and b.pos.pos < 178) or
                    (b.pos.pos > 280 and b.pos.pos < 302)):
                    velocita_limite = 8
                    if (b.velocita > velocita_limite):
                        b.decelera()
                else:
                    if (b.velocita < b.cavallo.vel_max*.5): # lo scosso va al massimo alla meta`
                        b.accelera()
        
            # stanchezza
            if (b.velocita > b.cavallo.vel_max*0.9):
                b.riserva -= 2
            else:
                b.riserva  -= 1
        

if __name__ == "__main__":
    nomi = ("Panezio", "Benito", "Zuccher", "Rimini", "Uberto", "Danubio", "Zodiach", "Pytheos", "Gallegg", "Figaro")

    engine = Engine(nomi)
    #for e in engine.barberi:
    #    print e.cavallo.nome, e.cavallo.vel_max
    
    engine.loadMap()
    engine.mossa()

    while 1:
        engine.move()
        engine.ordinaBarberi()
        direzioni = []
        print "--------------"
        for b in engine.barberi:
            #print "%s\t\t %d %d %d"%(b.cavallo.nome, b.pos.pos, b.pos.val, b.velocita)
            direzioni.append(b.traiettoria)
        #print direzioni
