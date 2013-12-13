#! /usr/bin/env python

import sys
import math
import pyglet
from pyglet.gl     import * 
from pyglet.window import key

import simulation

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


# background
background = pyglet.resource.image("background.jpeg")
foreground = pyglet.resource.image("foreground.png")

# world
#world = engine.World((1600, 1200))
#world.setBackgroundColor(black)
#world.addBackgroundImage(background, (0, 0))
#world.addForegroundImage(foreground, (0, 0))

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

# 
targets = [ 14, 150, 178, 280, 302,277 ]

# sprites
batch = pyglet.graphics.Batch()

red_image = pyglet.resource.image("red_arrow.png")
red_image.anchor_x = red_image.width  // 2
red_image.anchor_y = red_image.height // 2

blue_image = pyglet.resource.image("blue_arrow.png")
blue_image.anchor_x = blue_image.width  // 2
blue_image.anchor_y = blue_image.height // 2

green_image = pyglet.resource.image("green_arrow.png")
green_image.anchor_x = green_image.width  // 2
green_image.anchor_y = green_image.height // 2

scale = 0.02
angle = math.pi / 2.

sprites = []
for i in xrange(len(worldmap.points)):
  if worldmap.points[i].index in targets:
    sprite = pyglet.sprite.Sprite(red_image, batch = batch)
  elif worldmap.points[i].value == 0:
    sprite = pyglet.sprite.Sprite(blue_image, batch = batch)
  else:
    sprite = pyglet.sprite.Sprite(green_image, batch = batch)
  sprite.rotation = angle
  sprite.scale    = scale
  sprites.append(sprite)

movers = [ simulation.BarberoStatic(sprite, worldmap) for sprite in sprites ]
animator = Animator(movers)
pyglet.clock.schedule_interval(animator.update, 1./60)    # 60 Hz


@window.event
def on_draw():
  window.clear()
  background.blit(0,0)
  batch.draw()

@window.event
def on_key_press(symbol, modifiers):
  if symbol == key.ESCAPE:
    pyglet.app.exit()
  elif symbol == key.F11:
    window.set_fullscreen(not window.fullscreen)

pyglet.app.run()
