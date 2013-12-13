import random 
import sys

class Cavallo:
    def __init__(self, n):
        self.nome = n
        self.scatto = 1
        self.vel_max = int(random.uniform(40, 60))
        self.resistenza = int(random.uniform(50,100))
        self.precisione = int(random.uniform(0,4))
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
    if ((b1.pos.pos <= b2.pos.pos) or
        ((b1.pos.pos == b2.pos.pos) and (b1.pos.val > b2.pos.val))):
        return 1
    return -1

class Engine():
    def __init__(self, n):
        self.barberi = [Barbero(n[i], i) for i in xrange(10)]    
        self.piazza = []
        self.ordine = []

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
                    return h+0
                elif (dy == 1):
                    return h+2
                elif (dy == 0 and dx == -2):
                    return h+4
                elif (dy == 0 and dx == -1):
                    return h+8
                elif (dy == 0 and dx == 0):
                    return h+9999
                else:
                    return h+2
            else:
                return 9999


    def move(self):
        for b in self.barberi:
            #print b.cavallo.nome

            turns = [-1, 0, 1]
            paths = [[self.handicap(l, b.cavallo.precisione), turns[j], l] for j,l in enumerate(b.pos.leafs) if (l != -1)]
            #print "start"
            #print paths
            for iteration in xrange(int(b.velocita*1.25)):
                temp_paths = []
                for path in paths:
                    current_val = self.piazza[path[-1]].val
                    for leaf in self.piazza[path[-1]].leafs:    
                        #print leaf
                        if (leaf != -1):
                            deltaX = -current_val+self.piazza[leaf].val
                            if (deltaX * path[1] < 0):
                                continue
                                
                            new_leaf = leaf
                            #print b.velocita -iteration
                            for i in xrange(int(b.velocita*1.25)-iteration):
                                new_leaf = self.piazza[new_leaf].leafs[1]
                                #print new_leaf,
                                if (new_leaf == -1):
                                    break
                            #print "new_leaf",new_leaf
                            if (new_leaf == -1):
                                continue
                            temp_paths.append([path[0]+self.handicap(leaf, b.cavallo.precisione)] + [turns] + path[2:]+[leaf])

                # cleaning
                temp_paths = sorted(temp_paths, key=lambda paths:-paths[0])
                #print "temp_paths"
                #print temp_paths
                paths = temp_paths[0:2]
                #print paths
                #print len(paths), b.pos.val, b.pos.pos

            # velocita
            if (b.scosso):
                b.velocita = b.velocita-(b.pos.val*.25)
                if (b.velocita < 0):
                    b.velocita = 0
                #print paths[0]
                #print b.velocita, len(paths[0]), int(b.velocita)+2, int(int(b.velocita)/2)+2
                b.pos = self.piazza[paths[0][int(b.velocita)+2]]
                b.traiettoria = paths[0][2:]

                if ((b.pos.pos > 150 and b.pos.pos < 180) or
                    (b.pos.pos > 240 and b.pos.pos < 260)):
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
    nomi = ("Panezio", "Benito", "Zucchero", "Rimini", "Uberto", "Danubio", "Zodiach", "Pytheos", "Galleggiante", "Figaro")

    engine = Engine(nomi)
    for e in engine.barberi:
        print e.cavallo.nome, e.cavallo.vel_max
    

    engine.loadMap()
    engine.mossa()

    for z in xrange(40):
        engine.move()
        engine.ordinaBarberi()
        direzioni = []
        print "--------------"
        for b in engine.barberi:
            print b.cavallo.nome, b.pos.pos, b.velocita
            temp = [b.indice]
            for i,j in enumerate(b.traiettoria):
                temp += [float(i)/float(len(b.traiettoria)), engine.piazza[j].coord]
            direzioni.append(temp)
        #print direzioni

