import math
import random
import pygame

# fallback for backwards compatibility
if not 'smoothscale' in pygame.transform.__dict__:
  pygame.transform.smoothscale = pygame.transform.scale

class World(object):
  def __init__(self, size):
    # world size, in worls coordinates
    self.frame = pygame.Rect((0,0), size)
    self.image = None
    # background color
    self.background = (0, 0, 0)     # black
    # stack of background images
    self.images = []
    self.ontops = []

  def setBackgroundColor(self, color):
    self.background = color
    self.image = None

  def addBackgroundImage(self, image, position):
    # add a background image
    # "image"     can be any blittable surface
    # "position"  gives the image position, in world oordinates
    self.images.append((image, position))
    self.image = None

  def addForegroundImage(self, image, position):
    self.ontops.append((image, position))
    self.ontop = None

  def resetBackgroundImages(self):
    self.images = []
    self.image = None

  def draw(self):
    if self.image is None:
      # render the backgound
      self.image = pygame.Surface((self.frame.w, self.frame.h))
      self.image.fill(self.background)
      for image, pos in self.images:
        self.image.blit(image, pos)
    return self.image

  def draw_fg(self):
    if self.ontop is None:
      # render the backgound
      self.ontop = pygame.Surface((self.frame.w, self.frame.h), pygame.SRCALPHA)
      for ontop, pos in self.ontops:
        self.ontop.blit(ontop, pos)
    return self.ontop

  # draw the world through the viewport
  def render(self, viewport):
    # find the intersection between the 'world' and the 'view'
    view = self.frame.clip(viewport.inner)
    subs = self.draw().subsurface(view)
    rect = pygame.Rect( 
      (view.x - viewport.inner.x) / viewport.scale,
      (view.y - viewport.inner.y) / viewport.scale,
      view.w / viewport.scale,
      view.h / viewport.scale )
    surf = pygame.transform.smoothscale(subs, rect.size)
    return surf, rect

  def render_fg(self, viewport):
    # find the intersection between the 'world' and the 'view'
    view = self.frame.clip(viewport.inner)
    subs = self.draw_fg().subsurface(view)
    rect = pygame.Rect( 
      (view.x - viewport.inner.x) / viewport.scale,
      (view.y - viewport.inner.y) / viewport.scale,
      view.w / viewport.scale,
      view.h / viewport.scale )
    surf = pygame.transform.smoothscale(subs, rect.size)
    return surf, rect
    



class Viewport(object):
  def __init__(self, size, world):
    self.frame = pygame.Rect((0,0), size)   # frame size, in screen coordinates
    self.world = world
    self.inner = world.frame                # area to be shown in the frame, in world coordinates - default to the whole world, clamped to the frame aspect ratio
    self.offset = (0,0)
    self.history = []
    self.constrain()

  def center(self, wx, wy):
    # center the viewport on the (wx, wy) world coordinates
    area = self.inner.copy()
    area.center = (round(wx), round(wy))
    self.pan(area)
    self.constrain()

  def pan(self, area):
    # pan and zoom the viewport to show the area
    self.history.append(area.copy())
    if len(self.history) > 10:
      del self.history[0]
    x = round(sum(h.x for h in self.history) / len(self.history))
    y = round(sum(h.y for h in self.history) / len(self.history))
    w = round(sum(h.w for h in self.history) / len(self.history))
    h = round(sum(h.h for h in self.history) / len(self.history))
    self.inner = pygame.Rect((x, y), (w, h))
    self.constrain()

  def resize(self, size):
    # resize the viewport, trying to keep the same world scaling
    self.frame.size = size
    self.inner.w = round(self.frame.w * self.scale)
    self.inner.h = round(self.frame.h * self.scale)
    self.constrain()

  # adapt the viewport "inner" position to match the "frame" aspect ration, and be inside the world
  def constrain(self):
    # if both dimensions are greated than the world size, reduce the view to the wole world
    if self.inner.w > self.world.frame.w and self.inner.h > self.world.frame.h:
      self.inner = self.world.frame.copy()

    # expand the view to match the frame aspect ratio
    sw = float(self.inner.w) / float(self.frame.w)
    sh = float(self.inner.h) / float(self.frame.h)
    self.scale = max(sw, sh)
    self.inner.h = round(self.frame.h * self.scale)
    self.inner.w = round(self.frame.w * self.scale)

    # clamp the view back inside the world, if possible
    self.inner.clamp_ip( self.world.frame )


  def transform(self, wx, wy):
    # transform a pair of world coordinates into viewport coordinates
    x = round((wx - self.inner.x) / self.scale)
    y = round((wy - self.inner.y) / self.scale)
    return (x, y)


    
  # pan the viewport to keep the sprites in the field of view
  def look_at(self, sprites):
    x = min([sprite.x for sprite in sprites])
    y = min([sprite.y for sprite in sprites])
    w = max([sprite.x for sprite in sprites]) - x
    h = max([sprite.y for sprite in sprites]) - y

    # add some border: bounding boxes, plus 10% in each direction
    buf_w = 0.2 * w + max([sprite.w * sprite.scale for sprite in sprites])
    buf_h = 0.2 * h + max([sprite.h * sprite.scale for sprite in sprites])
    x = round(x - buf_w / 2.)
    y = round(y - buf_h / 2.)
    w = round(w + buf_w)
    h = round(h + buf_h)

    self.pan( pygame.Rect((x, y), (w, h)) )


class Sprite(object):
  def __init__(self):
    # which image, and how to render it (rotozoom)
    self.image = None
    self.scale = 1.
    self.angle = 0.
    # position, in world coordinates (need floats, can't use Rect)
    self.x = 0.
    self.y = 0.
    # hotspot, in local (image) coordinates, used as reference point for movement and rotations
    self.center_x = 0.
    self.center_y = 0.
    # size, in local (image) coordinates
    self.w = 0.
    self.h = 0.
    # rendered image
    self.surf = None
    self.rect = None

  def setImage(self, image, (x, y), scale, angle):
    # set the image, scaling and rotation (transform from image to world coordinates)
    self.image = image
    self.scale = scale
    self.angle = angle
    # set the hotspot (in image coordinates)
    self.center_x = x
    self.center_y = y
    # size, in local (image) coordinates
    self.w = self.image.get_width()
    self.h = self.image.get_height()

  def setPosition(self, x, y, angle):
    # position, in world coordinates
    self.x = x
    self.y = y
    # angle
    self.angle = angle

  def render(self, viewport):
    # XXX optimize: some operations should be done only if the relevant parameter have changed
    scale = self.scale / viewport.scale

    # cache sin and cos values
    _s = math.sin(self.angle)
    _c = math.cos(self.angle)
 
    # hotspot - center, in local coordinates
    dx = self.center_x - self.w / 2.
    dy = self.center_y - self.h / 2.

    # hotspot - center, in world coordinates
    wdx = (dx * _c - dy * _s) * self.scale
    wdy = (dx * _s + dy * _c) * self.scale 
   
    # position of the hotspot in viewport coordinates
    surf = pygame.transform.rotozoom( self.image, math.degrees(self.angle), scale )
    rect = surf.get_rect( center = viewport.transform(self.x + wdx, self.y + wdy) )
    return surf, rect

