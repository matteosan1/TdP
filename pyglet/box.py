#! /usr/bin/env python

import sys
import math
import random

import pyglet
from pyglet.window import key

import simulation
import engine

class Animator(object):
  def __init__(self, items):
    self.items = items
    for index, item in enumerate(self.items):
      item.init(index)

  def update(self, delta):
    for index, item in enumerate(self.items):
      item.update(index, delta)


pyglet.resource.path = [ 'res' ]
pyglet.resource.reindex()


# contrade
names = [
    'aquila',
    'bruco',
    'chiocciola',
    'civetta',
    'drago',
    'giraffa',
    'istrice',
    'leocorno',
    'lupa',
    'nicchio',
    'oca',
    'onda',
    'pantera',
    'selva',
    'tartuca',
    'torre',
    'valdimontone' ]

# background
background = pyglet.resource.image("background.jpeg")
foreground = pyglet.resource.image("foreground.png")

# parametrized world map
worldmap = simulation.WorldMap()
worldmap.load('res/mappa_piazza.csv')

# initialize the window to the viewport
config = pyglet.gl.Config(
    double_buffer = True,
    alpha_size    = 8)
window = pyglet.window.Window(
    fullscreen    = True,
    resizable     = True,
    vsync         = True,
    config        = config ) 
window.set_caption('Tempo di Palle')
window.set_icon(pyglet.resource.image('ball.png'))

# load models
batch = pyglet.graphics.Batch()

scale = 0.2
angle = math.pi / 2.

def load_frames(name):
  image = pyglet.resource.image(name)
  image.anchor_x = image.width  // 2
  image.anchor_y = image.height // 2
  grid = pyglet.image.ImageGrid(image, 10, 10)
  texture = pyglet.image.TextureGrid(grid)
  return texture

frames  = [ load_frames('%s.png' % name) for name in names ]

# "random movement"
sprites  = [ engine.Sprite(random.choice(frames), batch = batch) for i in xrange(100) ]
for sprite in sprites:
  sprite.rotation = angle
  sprite.scale    = scale
movers   = [ simulation.BoundMover(sprite, (0,0, 1600, 1200)) for sprite in sprites ]

animator = Animator(movers)
pyglet.clock.schedule_interval(animator.update, 1./60)    # 60 Hz

world_box = engine.Rect(0, 0, 1600, 1200)
view = engine.View(window, world_box)

follow = False

@window.event
def on_draw():
  if follow:
    view.look_at( sprites )
  else:
    view.move(0, 0, 1600, 1200)

  window.clear()
  #pyglet.gl.glViewport(-x, -y, w, h)
  pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
  pyglet.gl.glLoadIdentity()
  # moved inside engine.View.glApply()
  # pyglet.gl.glOrtho(x1, x2, y1, y2, -1, 1)
  view.glApply()
  pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
  background.blit(0,0)
  batch.draw()


@window.event
def on_resize(x, y):
  view.window_resize()

@window.event
def on_key_press(symbol, modifiers):
  if symbol == key.ESCAPE:
    pyglet.app.exit()
  elif symbol == key.F11:
    window.set_fullscreen(not window.fullscreen)
  elif symbol == key.SPACE:
    global follow
    follow = not follow


pyglet.app.run()
