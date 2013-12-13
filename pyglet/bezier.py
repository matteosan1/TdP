# modified from http://cs.nyu.edu/exact/core/download/core_v1.8/core_v1.8/python/progs/bezier/bezier.py
#
# $Id: bezier.py,v 1.2 2005/05/09 21:16:28 exact Exp $
# 
# see http://www.doc.ic.ac.uk/~dfg/AndysSplineTutorial/Beziers.html 
# for an interactive bezier drawing applet

from math import *

# class Point
class Point:
	def __init__(self, x = 0.0, y = 0.0):
		self.x = float(x)
		self.y = float(y)
	
	def distance(self, p):
		return sqrt((p.x-self.x)*(p.x-self.x)+(p.y-self.y)*(p.y-self.y))

	def length(self):
		return self.distance(Point(float(0), float(0)))

	def towards(self, target, t):
		return Point((1.0-t)*self.x+t*target.x, (1.0-t)*self.y+t*target.y)
	
	def __sub__(self, p):
		return Point(self.x-p.x, self.y-p.y)

	def __add__(self, p):
		return Point(self.x+p.x, self.y+p.y)

	def __mul__(self, c):
		return Point(c*self.x, c*self.y)

	def __eq__(self, p):
		return self.x == p.x and self.y == p.y

	def __ne__(self, p):
		return not (self == p)
	
 	def __repr__(self):
 		return "Point(%s, %s)" % (self.x, self.y)  	
 

# class Bezier
class Bezier():
	def __init__(self, v):
		self.deg = len(v) - 1
		self.cp  = [ Point(x, y) for (x, y) in v ]
	
	def getPoint(self, t):
		curr = [0] * self.deg
		# get initial
		for i in range(self.deg):
			curr[i] = self.cp[i].towards(self.cp[i+1], t)
		for i in range(self.deg-1):
			for j in range(self.deg-1-i):
				curr[j] = curr[j].towards(curr[j+1], t)
		return curr[0]


def interpolate(points, steps):
  bc = Bezier(points)
  dt = 1. / steps
  t  = 0.
  
  out = []
  for i in xrange(steps+1):
    t = float(i) / steps
    p = bc.getPoint(t)
    out.append( (p.x, p.y) )
  return out


def main():
  points = [ (0., 0.), 
             (1., 0.), 
             (2., 0.),
             (3., 1.), 
             (4., 1.), 
             (5., 1.) ]
  p = interpolate(points, 20)
  for (x, y) in p:
    print '%0.3f, %0.3f' % (x, y)



if __name__ == "__main__":
  main()
