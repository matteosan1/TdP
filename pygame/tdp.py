#! /usr/bin/env python

import sys
import math
import random
import pygame

import engine_pygame as engine
import simulation

def main():
  pygame.init()
  time = pygame.time.get_ticks()

  # background
  black = (0, 0, 0)
  background = pygame.image.load("res/background.jpeg")
  foreground = pygame.image.load("res/foreground.png")

  # world
  world = engine.World((1600, 1200))
  world.setBackgroundColor(black)
  world.addBackgroundImage(background, (0, 0))
  world.addForegroundImage(foreground, (0, 0))

  # parametrized world map
  worldmap = simulation.WorldMap()
  worldmap.load('res/mappa_piazza.csv')

  # initialize the window to the viewport
  screen = pygame.display.set_mode( (800, 600), pygame.RESIZABLE )

  # viewport size and position, in world coordinates
  viewport = engine.Viewport(screen.get_size(), world)
  viewport.pan(world.frame)

  # sprites
  red = engine.Sprite()
  image = pygame.image.load("res/red_arrow.png")
  (x,y) = image.get_rect().center
  scale = 0.1
  angle = math.pi / 2.
  red.setImage(image, (x,y), scale, angle)

  blue = engine.Sprite()
  image = pygame.image.load("res/blue_arrow.png")
  (x,y) = image.get_rect().center
  scale = 0.1
  angle = math.pi / 2.
  blue.setImage(image, (x,y), scale, angle)

  greens = [ engine.Sprite() for i in range(8) ]
  for green in greens:
    image = pygame.image.load("res/green_arrow.png")
    (x,y) = image.get_rect().center
    scale = 0.1
    angle = math.pi / 2.
    green.setImage(image, (x,y), scale, angle)

  sprites = []
  sprites.append(red)
  sprites.append(blue)
  sprites.extend(greens)

  interest = []
  interest.append(red)
  interest.append(blue)

  movers = [ simulation.BarberoMover(sprite, worldmap) for sprite in sprites ] 
  #movers = [ simulation.BoundMover(sprite, world.frame) for sprite in sprites ] 

  time = pygame.time.get_ticks()
  for id, mover in enumerate(movers):
    mover.init(time, id)
    #mover.init(time)

  # clock
  clock = pygame.time.Clock()

  # event loop
  while True:
      clock.tick()
      time = pygame.time.get_ticks()
      #print( clock.get_fps() )

      # monitor events
      for event in pygame.event.get():
          if event.type == pygame.VIDEORESIZE:
              screen = pygame.display.set_mode( event.size, pygame.RESIZABLE )
              viewport.resize( screen.get_size() )
          elif event.type == pygame.QUIT: 
              sys.exit()

      # update the position of the sprites
      for mover in movers: 
        mover.update(time)

      #viewport.look_at(interest)

      # render the background and the sprites
      screen.fill(black)
      screen.blit(*world.render(viewport))
      for sprite in sprites:
        screen.blit(*sprite.render(viewport))
      screen.blit(*world.render_fg(viewport))
      pygame.display.flip()


if __name__ == "__main__":
    main()
