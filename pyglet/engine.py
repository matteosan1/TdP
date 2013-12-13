import pyglet

class Rect(object):
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.width = w
    self.height = h

class View(object):
  def __init__(self, window, world):
    self.x = world.x
    self.y = world.y
    self.width = world.width
    self.height = world.height
    self.scale = 1.
    self.window = window
    self.world  = world
    self.fix()

  def glApply(self):
    pyglet.gl.glOrtho(
      int(round(self.x)),
      int(round(self.x + self.width)),
      int(round(self.y)),
      int(round(self.y + self.height)),
      -1, 1)

  # pan the viewport
  def pan(self, x, y):
    self.x = x
    self.y = y
    self.fix()

  # zoom the viewport
  def zoom(self, scale):
    self.scale = scale
    self.fix()

  # resize the viewport, trying to keep the same viewpoint and scale factor
  def resize(self, w, h):
    x = self.x + self.width / 2
    y = self.y + self.height / 2
    self.width = w
    self.height = h
    self.x = x - self.width / 2
    self.y = y - self.height / 2
    self.fix()

  # resize the viewport, trying to keep the same viewpoint and scale factor
  def window_resize(self):
    self.resize(self.window.width  * self.scale, self.window.height * self.scale)

  # pan and zoom the viewport
  def move(self, x, y, w, h):
    self.x = x
    self.y = y
    self.width = w
    self.height = h
    self.fix()

  # pan and zoom the viewport to keep the sprites in the field of view
  def look_at(self, sprites):
    border = 100
    self.x = min([sprite.x for sprite in sprites])          - border
    self.y = min([sprite.y for sprite in sprites])          - border
    self.width = max([sprite.x for sprite in sprites]) - self.x + border
    self.height = max([sprite.y for sprite in sprites]) - self.y + border
    self.fix()

  # adapt the viewport "inner" position to match the "frame" aspect ration, and be inside the world
  def fix(self):
    # expand the view to match the frame aspect ratio
    sw = float(self.width) / float(self.window.width)
    sh = float(self.height) / float(self.window.height)
    self.scale = max(sw, sh)
    dw = self.window.width  * self.scale - self.width
    dh = self.window.height * self.scale - self.height
    self.x -= dw / 2
    self.y -= dh / 2
    self.width += dw 
    self.height += dh

    # clamp the view back inside the world, if possible
    if self.width > self.world.width:
      self.x = (self.world.width - self.width) / 2 
    elif self.x < 0:
      self.x = 0
    elif self.x + self.width > self.world.width:
      self.x = self.world.width - self.width

    if self.height > self.world.height:
      self.y = (self.world.height - self.height) / 2 
    elif self.y < 0:
      self.y = 0
    elif self.y + self.height > self.world.height:
      self.y = self.world.height - self.height


class Sprite(pyglet.sprite.Sprite):
  def __init__(self, frames, **kargs):
    self.frames = frames
    self.frame  = 0
    image = self.frames[0]
    super(Sprite, self).__init__(image, **kargs)

  def next_frame(self):
    self.frame = (self.frame + 1) % len(self.frames)
    self.image = self.frames[self.frame]
    self.image.anchor_x = self.image.width  // 2
    self.image.anchor_y = self.image.height // 2

    

