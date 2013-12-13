import math
import random
import bezier

class BoundMover(object):
  PIXEL_PER_FRAME = 276.46 / 100 
  RANDOMIZE_EVERY = 10

  def __init__(self, sprite, box):
    self.sprite = sprite
    self.box    = box

    # (x, y) center coordinates, taken from sprite and scale
    self.x = 0.
    self.y = 0.
    self.speed = 0.
    self.angle = 0.
    self.velocity = [ 0., 0. ]
    self.step_s = 0.
    self.step_t = 0.
    self.render()

  def init(self, index):
    self.x      = random.uniform(self.box[0], self.box[2])
    self.y      = random.uniform(self.box[1], self.box[3])
    self.speed  = random.gauss(50., 1.)
    self.angle  = random.uniform( -math.pi, math.pi )
    self.velocity = [ self.speed * math.cos(self.angle), -self.speed * math.sin(self.angle) ]
    self.render()

  def render(self):
    self.sprite.x = self.x
    self.sprite.y = self.y
    self.sprite.rotation = math.degrees(self.angle)

  def update(self, index, delta):
    self.x += self.velocity[0] * delta
    self.y += self.velocity[1] * delta
    self.step_s += self.speed * delta / self.PIXEL_PER_FRAME / self.sprite.scale
    while (self.step_s > 1):
      self.step_s -= 1
      self.sprite.next_frame()
    self.step_t += self.speed * delta / self.RANDOMIZE_EVERY
    while (self.step_t > 1):
      self.step_t -= 1
      self.angle += random.gauss(0., 0.1)
      self.velocity = [ self.speed * math.cos(self.angle), -self.speed * math.sin(self.angle) ]

    if self.x < self.box[0]:
      self.x = 2 * self.box[0] - self.x
      self.angle = math.pi - self.angle
      self.velocity[0]  = -self.velocity[0]
    elif self.x > self.box[2]:
      self.x = 2 * self.box[2] - self.x
      self.angle = math.pi - self.angle
      self.velocity[0]  = -self.velocity[0]
    if self.y < self.box[1]:
      self.y = 2 * self.box[1] - self.y
      self.angle = - self.angle
      self.velocity[1]  = - self.velocity[1]
    elif self.y > self.box[3]:
      self.y = 2 * self.box[3] - self.y
      self.angle = - self.angle
      self.velocity[1]  = - self.velocity[1]

    self.render()


class WorldPoint:
    def __init__(self, p = None):
      if p is None:
        self.coord = (0,0)
        self.angle = 0.
        self.value = 0
        self.index = 0
        self.leafs = (-1, -1, -1)
      else:
        self.coord = (p[0], p[1])
        self.angle = p[2]
        self.value = p[3]
        self.index = p[4]
        self.leafs = (p[5], p[6], p[7])


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


class BarberoStatic(object):
  def __init__(self, sprite, worldmap):
    self.worldmap = worldmap
    self.sprite = sprite

    self.index  = -1
    self.center = (0., 0.)
    self.angle  =  0.
    self.speed  =  0.

  # update the sprite
  def render(self):
    self.sprite.x = 155 + self.center[0] * 1.15625
    self.sprite.y = -40 + self.center[1]
    self.sprite.rotation = math.degrees(-self.angle)

  # mossa
  def init(self, index):
    self.index  = index
    self.center = self.worldmap.points[self.index].coord
    self.angle  = self.worldmap.points[self.index].angle
    self.render()

  # make a step
  def update(self, index, delta):
    self.render()


class BarberoMover(object):
  PIXEL_PER_FRAME = 276.46 / 100 

  def __init__(self, sprite, worldmap):
    self.worldmap   = worldmap
    self.sprite     = sprite

    self.prev_curve   = None
    self.next_curve   = None
    self.past_indices = []      # list of (t, index)
    self.next_indices = []      # list of (t, index)
    self.trajectory   = []      # list of (t, (x, y), angle)
    self.center = (0., 0.)      # current position
    self.angle  =  0.           # current direction
    self.time   =  0.
    self.speed  = random.gauss(50., 2.)

    # fractions of the current step and animation
    self.step_s = 0.
    self.time   = 0.

  # update the sprite
  def render(self):
    self.sprite.x = 155 + self.center[0] * 1.15625
    self.sprite.y = -40 + self.center[1]
    self.sprite.rotation = math.degrees(-self.angle)

  # mossa
  def init(self, index):
    self.step_s = 0.
    self.time   = 0.

    index  = 164 + index % 10
    self.past_indices = [ (0., index) ]
    self.next_indices = []
    self.center       = self.worldmap.points[index].coord
    self.angle        = self.worldmap.points[index].angle
    self.trajectory   = [ (0., self.center, self.angle) ]
    self.prev_curve   = None
    self.next_curve   = None
    self.choose_next()
    self.render()

  def choose_next_index(self, index):
    leafs = []
    for l in self.worldmap.points[index].leafs:
      if l == -1: 
        continue
      if self.worldmap.points[l].value == self.worldmap.points[index].value:
        leafs.extend( [l] * 10 )
      else:
        leafs.append(l)
    return random.choice( leafs )

  def choose_next(self):
    # move all past steps from next_indices to past_indices
    while self.next_indices and self.next_indices[0][0] < self.time:
      item = self.next_indices[0]
      self.past_indices.append(item)
      del self.next_indices[0]

    # fill the buffer with up to 10 steps
    if self.next_indices:
      prev = self.next_indices[-1]
    else:
      prev = self.past_indices[-1]
    while len(self.next_indices) < 10:
      next   = 0., self.choose_next_index(prev[1])
      prev_p = self.worldmap.points[prev[1]].coord
      next_p = self.worldmap.points[next[1]].coord
      length = math.hypot(next_p[0] - prev_p[0], next_p[1] - prev_p[1])
      next   = prev[0] + length / self.speed, next[1]
      self.next_indices.append(next)
      prev = next

    # the trajectory is defined as a linear interpolation between two bezier curves
    # each curve is generated from a central point (previouis and next control points) and the N-1 closest ones

    self.prev_curve = self.next_curve
    indices = self.past_indices[-4:] + self.next_indices[:3]
    self.next_curve = bezier.Bezier([self.worldmap.points[index[1]].coord for index in indices])
    self.next_curve.tmin = indices[0][0]
    self.next_curve.tmax = indices[-1][0]

    # update the trajectory
    steps  = 10
    if self.prev_curve is None:
      for i in range(1, steps + 1):
        t = self.past_indices[-1][0] + float(i) / steps * (self.next_indices[0][0] - self.past_indices[-1][0])
        tb_new = (t - self.next_curve.tmin) / (self.next_curve.tmax - self.next_curve.tmin)
        x = self.next_curve.getPoint(tb_new).x
        y = self.next_curve.getPoint(tb_new).y
        self.trajectory.append((t, (x, y)))
    else:
      for i in range(1, steps + 1):
        t = self.past_indices[-1][0] + float(i) / steps * (self.next_indices[0][0] - self.past_indices[-1][0])
        tb_old = (t - self.prev_curve.tmin) / (self.prev_curve.tmax - self.prev_curve.tmin)
        tb_new = (t - self.next_curve.tmin) / (self.next_curve.tmax - self.next_curve.tmin)
        x = self.prev_curve.getPoint(tb_old).x * (1. - float(i) / steps) + self.next_curve.getPoint(tb_new).x * (float(i) / steps)
        y = self.prev_curve.getPoint(tb_old).y * (1. - float(i) / steps) + self.next_curve.getPoint(tb_new).y * (float(i) / steps)
        self.trajectory.append((t, (x, y)))


  # make a step
  def update(self, index, delta):
    self.step_s += self.speed * delta / self.PIXEL_PER_FRAME / self.sprite.scale
    while (self.step_s > 1):
      self.step_s -= 1
      self.sprite.next_frame()

    self.time += delta
    while self.time > self.next_indices[0][0]:
      self.choose_next()

    past = [i for i, arg in enumerate(self.trajectory) if arg[0] < self.time]
    #if past:
    s = max(past)
    #else:
    #  s = 0
    prev = self.trajectory[s]
    next = self.trajectory[s+1]

    self.center = ((prev[1][0] * (next[0] - self.time) + next[1][0] * (self.time - prev[0])) / (next[0] - prev[0]), 
                   (prev[1][1] * (next[0] - self.time) + next[1][1] * (self.time - prev[0])) / (next[0] - prev[0]))
    self.angle  = math.atan2(next[1][1] - prev[1][1], next[1][0] - prev[1][0])
    self.render()

class BarberoMover_old(object):
  PIXEL_PER_FRAME = 276.46 / 100 

  def __init__(self, sprite, worldmap):
    self.worldmap   = worldmap
    self.sprite     = sprite

    self.prev_curve   = None
    self.next_curve   = None
    self.past_indices = []      # list of (t, index)
    self.next_indices = []      # list of (t, index)
    self.trajectory   = []      # list of (t, (x, y), angle)
    self.center = (0., 0.)      # current position
    self.angle  =  0.           # current direction
    self.time   =  0.
    self.speed  = random.gauss(50., 2.)

    # fractions of the current step and animation
    self.step_s = 0.
    self.time   = 0.

  # update the sprite
  def render(self):
    self.sprite.x = 155 + self.center[0] * 1.15625
    self.sprite.y = -40 + self.center[1]
    self.sprite.rotation = math.degrees(-self.angle)

  # mossa
  def init(self, index):
    self.step_s = 0.
    self.time   = 0.

    index  = 164 + index % 10
    self.past_indices = [ (0., index) ]
    self.next_indices = []
    self.center       = self.worldmap.points[index].coord
    self.angle        = self.worldmap.points[index].angle
    self.trajectory   = [ (0., self.center, self.angle) ]
    self.prev_curve   = None
    self.next_curve   = None
    self.choose_next()
    self.render()

  def choose_next_index(self, index):
    leafs = []
    for l in self.worldmap.points[index].leafs:
      if l == -1: 
        continue
      if self.worldmap.points[l].value == self.worldmap.points[index].value:
        leafs.extend( [l] * 10 )
      else:
        leafs.append(l)
    return random.choice( leafs )


  def choose_next(self):
    # move all past steps from next_indices to past_indices
    while self.next_indices and self.next_indices[0][0] < self.time:
      item = self.next_indices[0]
      self.past_indices.append(item)
      del self.next_indices[0]

    # fill the buffer with up to 10 steps
    if self.next_indices:
      prev = self.next_indices[-1]
    else:
      prev = self.past_indices[-1]
    while len(self.next_indices) < 10:
      next   = 0., self.choose_next_index(prev[1])
      prev_p = self.worldmap.points[prev[1]].coord
      next_p = self.worldmap.points[next[1]].coord
      length = math.hypot(next_p[0] - prev_p[0], next_p[1] - prev_p[1])
      next   = prev[0] + length / self.speed, next[1]
      self.next_indices.append(next)
      prev = next

    # the trajectory is defined as a linear interpolation between two bezier curves
    # each curve is generated from a central point (previouis and next control points) and the N-1 closest ones

    self.prev_curve = self.next_curve
    indices = self.past_indices[-4:] + self.next_indices[:3]
    self.next_curve = bezier.Bezier([self.worldmap.points[index[1]].coord for index in indices])
    self.next_curve.tmin = indices[0][0]
    self.next_curve.tmax = indices[-1][0]

    # update the trajectory
    steps  = 10
    if self.prev_curve is None:
      for i in range(1, steps + 1):
        t = self.past_indices[-1][0] + float(i) / steps * (self.next_indices[0][0] - self.past_indices[-1][0])
        tb_new = (t - self.next_curve.tmin) / (self.next_curve.tmax - self.next_curve.tmin)
        x = self.next_curve.getPoint(tb_new).x
        y = self.next_curve.getPoint(tb_new).y
        self.trajectory.append((t, (x, y)))
    else:
      for i in range(1, steps + 1):
        t = self.past_indices[-1][0] + float(i) / steps * (self.next_indices[0][0] - self.past_indices[-1][0])
        tb_old = (t - self.prev_curve.tmin) / (self.prev_curve.tmax - self.prev_curve.tmin)
        tb_new = (t - self.next_curve.tmin) / (self.next_curve.tmax - self.next_curve.tmin)
        x = self.prev_curve.getPoint(tb_old).x * (1. - float(i) / steps) + self.next_curve.getPoint(tb_new).x * (float(i) / steps)
        y = self.prev_curve.getPoint(tb_old).y * (1. - float(i) / steps) + self.next_curve.getPoint(tb_new).y * (float(i) / steps)
        self.trajectory.append((t, (x, y)))


  # make a step
  def update(self, index, delta):
    self.step_s += self.speed * delta / self.PIXEL_PER_FRAME / self.sprite.scale
    while (self.step_s > 1):
      self.step_s -= 1
      self.sprite.next_frame()

    self.time += delta
    while self.time > self.next_indices[0][0]:
      self.choose_next()

    past = [i for i, arg in enumerate(self.trajectory) if arg[0] < self.time]
    #if past:
    s = max(past)
    #else:
    #  s = 0
    prev = self.trajectory[s]
    next = self.trajectory[s+1]

    self.center = ((prev[1][0] * (next[0] - self.time) + next[1][0] * (self.time - prev[0])) / (next[0] - prev[0]), 
                   (prev[1][1] * (next[0] - self.time) + next[1][1] * (self.time - prev[0])) / (next[0] - prev[0]))
    self.angle  = math.atan2(next[1][1] - prev[1][1], next[1][0] - prev[1][0])
    self.render()
