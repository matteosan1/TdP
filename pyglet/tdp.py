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

def load_frames(name):
  image = pyglet.resource.image(name)
  grid = pyglet.image.ImageGrid(image, 10, 10)
  texture = pyglet.image.TextureGrid(grid)
  return texture

# layers
show_barberi = pyglet.graphics.Batch()
show_arrows  = pyglet.graphics.Batch()

# "barberi"
barberi = [ load_frames('%s.png' % name) for name in names ]
scale = 0.2
angle = 0.0

running = random.sample(barberi, 10)
running_sprites = [ engine.Sprite(frames, batch = show_barberi) for frames in running ]
for sprite in running_sprites:
  sprite.rotation = angle
  sprite.scale    = scale
movers   = [ simulation.BarberoMover(sprite, worldmap) for sprite in running_sprites ]

animator = Animator(movers)
pyglet.clock.schedule_interval(animator.update, 1./60)    # 60 Hz


# arrows
arrows = [ pyglet.resource.image(name) for name in ("red_arrow.png", "blue_arrow.png", "green_arrow.png")]
for arrow in arrows:
  arrow.anchor_x = arrow.width  // 2
  arrow.anchor_y = arrow.height // 2

arrow_targets = [ 14, 150, 178, 280, 302 ]
arrow_sprites = []
scale = 0.02
angle = 0.0
for i in xrange(len(worldmap.points)):
  if worldmap.points[i].index in arrow_targets:
    sprite = pyglet.sprite.Sprite(arrows[0], batch = show_arrows)
  elif worldmap.points[i].value == 0:
    sprite = pyglet.sprite.Sprite(arrows[1], batch = show_arrows)
  else:
    sprite = pyglet.sprite.Sprite(arrows[2], batch = show_arrows)
  sprite.rotation = angle
  sprite.scale    = scale
  arrow_sprites.append(sprite)
arrow_movers = [ simulation.BarberoStatic(sprite, worldmap) for sprite in arrow_sprites ]
arrow_animator = Animator(arrow_movers)

# world and engine
world_box = engine.Rect(0, 0, 1600, 1200)
view = engine.View(window, world_box)

# configuration
follow = False
debug  = False

@window.event
def on_draw():
  if follow:
    view.look_at( running_sprites )
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
  if debug:
    show_arrows.draw()
  show_barberi.draw()


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
  elif symbol == key.D:
    global debug
    debug = not debug


pyglet.app.run()
