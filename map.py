import random

from square import Square

class Node():
  def __init__(self, elev):
    self.elev = elev

class Map():
  def __init__(self, w, h):
    self.squares = [[None] * w for _ in range(h)]
    self.w, self.h = w, h
    for y in range(h):
      for x in range(w):
        if (x + y)%2 == 0:
          self.squares[y][x] = Square((x, y))
          #if y == 0 or y == h - 1:
          #  self.squares[y][x] = Square(10, random.randint(0, 2), random.randint(0, 2))

    for i in range(15):
      x, y = self.random()
      self.squares[y][x].elev += 1000 + random.randint(-250, 250)
      for sq in self.neighbors(x, y):
        sq.elev += 500 + random.randint(-250, 250)

    for i in range(5):
      x, y = self.random()
      self.squares[y][x].elev += 500 + random.randint(-250, 250)
      for sq in self.neighbors(x, y):
        sq.elev += 250 + random.randint(-125, 125)

    for i in range(40):
      x, y = self.random()
      self.squares[y][x].elev += 500 + random.randint(-250, 250)

    for i in range(200):
      x, y = self.random()
      if self.squares[y][x].elev > 0:
        self.squares[y][x].moist = random.randint(0, 2)
        self.squares[y][x].rock = random.randint(0, 2)

    for i in range(50):
      x, y = self.random()
      if self.squares[y][x].elev > 0:
        self.squares[y][x].improv = random.choice(['mirror', 'condenser', 'borehole', 'bunker', 'collector', 'mine'])
      else:
        self.squares[y][x].improv = random.choice(['platform', 'harness'])

    for i in range(200):
      x, y = self.random()
      self.squares[y][x].veg = random.choice(['farm', 'fungus', 'forest'])

    for i in range(10):
      x, y = self.random()
      self.squares[y][x].bonus = random.choice(['nutrient', 'mineral', 'energy'])

    '''
    for f in faction_keys:
      x, y = self.random()
      base = Base(self, f, "Base %d,%d" % (x, y))
      self.squares[y][x].base = base
    '''

    for y in range(h):
      for x in range(w):
        if (x + y)%2 == 0:
          pass 

    self.calc_nodes()
  
  #calc_rivers, calc_rainfall

  def random(self):
    x = random.randint(0, self.w-1)
    y = random.randint(0, (self.h/2)-1)*2 + (x % 2)
    return x, y

  def neighbors(self, x, y):
    directions = [(0, -2), (1, -1), (2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0), (-1, -1)]
    ncoords = [self.mapcoords(x + ox, y + oy) for ox, oy in directions if self.mapcoords(x + ox, y + oy)] 
    return [self.squares[sy][sx] for sx, sy in ncoords] 

  def calc_nodes(self):
    neighbor_nodes = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for y in range(self.h):
      for x in range(self.w):
        if (x + y)%2 == 1:
          ncoords = [self.mapcoords(x + ox, y + oy) for ox, oy in neighbor_nodes if self.mapcoords(x + ox, y + oy)] 
          neighbors = [self.squares[sy][sx] for sx, sy in ncoords] 
          elev = sum([sq.elev for sq in neighbors])/len(neighbors)
          for sq in neighbors:
            if sq.elev <= 0:
              elev = 0
          self.squares[y][x] = Node(elev)
    #self.dprint()

  def dprint(self):
    wd = 5
    for line in self.squares:
      for square in line:
        try: 
          print repr(square.elev).rjust(wd),
        except AttributeError:
          print " "*wd,
      print
  
  #these should get renamed 
  def mapcoords(self, x, y):
    if y >= 0 and y < self.h: 
      return (x % self.w), y
    else:
      return None

  def msquares(self, x, y):
    coords = self.mapcoords(x, y)
    if coords:
      x, y = coords
      return self.squares[y][x]
    return None
    if y >= 0 and y < self.h: 
      return self.squares[y][x % self.w]
    else:
      return None

  def tsquare(self, (x, y)):
    return self.msquares(x, y)

  def tmcoor(self, (x, y)):
    return self.mapcoords(x, y)

  def mcoor_lst(self, origin, lst):
    x, y = origin
    return [self.mapcoords(x + ex, y + ey) for ex, ey in lst if self.mapcoords(x + ex, y + ey)]


