import math
import random
import pygame

class BoundMover(object):
  def __init__(self, sprite, box):
    self.sprite = sprite
    self.box    = box
    self.time   = None

    # (x, y) center coordinates, taken from sprite and scale
    self.x = 0.
    self.y = 0.
    self.speed = 0.
    self.angle = 0.
    self.velocity = [ 0., 0. ]
    self.sprite.setPosition( self.x, self.y, self.angle )

  def init(self, time, rect = None):
    self.time = time
    if rect is None:
      self.x = random.uniform(self.box.left, self.box.right)
      self.y = random.uniform(self.box.top,  self.box.bottom)
    else:
      self.x = random.uniform(rect.left, rect.right)
      self.y = random.uniform(rect.top,  rect.bottom)
    self.speed = random.gauss(0.5, 0.1)
    self.angle = random.uniform( -math.pi, math.pi )
    self.velocity  = [ self.speed * math.cos(self.angle), -self.speed * math.sin(self.angle) ]
    self.draw()

  def draw(self):
    self.sprite.setPosition( self.x, self.y, self.angle )

  def update(self, time):
    delta = time - self.time
    self.time = time

    self.x += self.velocity[0] * delta
    self.y += self.velocity[1] * delta

    if self.x < self.box.left:
      self.x = 2 * self.box.x - self.x
      self.angle = math.pi - self.angle
      self.velocity[0]  = -self.velocity[0]
    elif self.x > self.box.right:
      self.x = 2 * self.box.right - self.x
      self.angle = math.pi - self.angle
      self.velocity[0]  = -self.velocity[0]
    if self.y < self.box.top:
      self.y = 2 * self.box.top - self.y
      self.angle = - self.angle
      self.velocity[1]  = - self.velocity[1]
    elif self.y > self.box.bottom:
      self.y = 2 * self.box.bottom - self.y
      self.angle = - self.angle
      self.velocity[1]  = - self.velocity[1]

    self.draw()


class WorldPoint:
    def __init__(self, p = None):
      if p is None:
        self.coord  = (0,0)
        self.angle  = 0.
        self.length = 0
        self.index  = 0
        self.leafs  = (-1, -1, -1)
      else:
        self.coord  = (p[0], p[1])
        self.angle  = p[2]
        self.length = p[3]
        self.index  = p[4]
        self.leafs  = (p[5], p[6], p[7])


class WorldMap(object):
  def __init__(self):
    self.points = []

  def load(self, filename):
    format = (int, int, float, int, int, int, int, int)
    with open(filename, 'r') as f:
      for line in f:
        fields  = line.strip().split(',')
        numbers = map(lambda f, n: f(n), format, fields)
        self.points.append( WorldPoint(numbers) )


class BarberoMover(object):
    def __init__(self, sprite, worldmap):
      self.worldmap = worldmap
      self.sprite = sprite

      self.index  = -1
      self.center = (0., 0.)
      self.angle  =  0.
      self.speed  = random.gauss(1., 0.1) / 50.

      # fraction of the current step
      self.step   =  0.

    # update the sprite
    def draw(self):
      self.sprite.setPosition( 140 + self.center[0] * 1.2, 1240 - self.center[1], self.angle )

    # mossa
    def init(self, time, index):
      self.time   = time
      self.index  = 10 + index
      self.center = self.worldmap.points[self.index].coord
      self.angle  = self.worldmap.points[self.index].angle
      self.step   =  0.
      self.choose_next()
      self.draw()

    def choose_next(self):
      leafs = [ id for id in self.worldmap.points[self.index].leafs if id != -1 ]
      self.next = random.choice( leafs )

    # make a step
    def update(self, time):
      delta = time - self.time
      self.time = time
      self.step += delta * self.speed
      while (self.step > 1.):
        self.step -= 1.
        self.index = self.next
        self.choose_next()

      prev_p = self.worldmap.points[self.index].coord
      prev_a = self.worldmap.points[self.index].angle
      next_p = self.worldmap.points[self.next].coord
      next_a = self.worldmap.points[self.next].angle
      self.center = (prev_p[0] * (1. - self.step) + next_p[0] * self.step, 
                     prev_p[1] * (1. - self.step) + next_p[1] * self.step)
      self.angle  = (prev_a    * (1. - self.step) + next_a    * self.step)
      self.draw()

