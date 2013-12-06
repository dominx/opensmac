import random
import copy
from pygame.rect import Rect
import cPickle as pickle
import zlib

from widget import *
import img
import loop
import rules

class DetailedValue():
  def __init__(self, val = 0, desc = ''):
    self.val = val
    self.detail = [(val, desc)]
  def add(self, n, desc):
    self.val += n
    self.detail.append((self.val, desc + (" %+d" % n)))
  def imul(self, n, desc):
    self.val = int(self.val * n)
    self.detail.append((self.val, desc + (" *%.1f" % n)))
  def cap(self, n, desc):
    self.val = min(self.val, n)
    self.detail.append((self.val, desc + (" <=%d" % n)))
  def lcap(self, n, desc):
    self.val = max(self.val, n)
    self.detail.append((self.val, desc + (" >=%d" % n)))
  def copy(self):
    return copy.copy(self)

class Square():
  def __init__(self, pos):
    self.pos = pos
    self.elev = 0
    self.rock = 0
    self.moist = 0
    self.bonus = None
    self.improv = None
    self.road = None
    self.veg = None
    self.base = None
    self.worked = False

  def __repr__(self):
    return str(self.pos)

  #todo restrictions, buildings, projects, tech
  # add_improv, rem_improv
  def nutrient(self, base = None, faction = None):
    if base: faction = base.faction
    nuts = DetailedValue(0)
    if self.base:
      nuts.add(2, 'base square')
    else:
      if self.bonus == 'nutrient':
        nuts.add(2, 'bonus')
      if self.elev > 0:
        if self.veg == 'fungus':
          nuts.cap(0, 'fungus')
        elif self.veg == 'forest':
          nuts.add(1, 'forest')
        else:
          nuts.add(self.moist, 'moisture')
          if self.veg == 'farm':
            nuts.add(1, 'farm')
          if self.veg == 'enricher':
            nuts.add(1, 'farm')
            nuts.imul(1.5, 'enricher')
          if self.improv == 'condenser':
            nuts.imul(1.5, 'condenser')
        if self.improv == 'mine':
          #if nuts.val > 0:
          nuts.add(-1, 'mine')
          nuts.lcap(0, '')
        if self.improv == 'borehole':
          nuts.cap(0, 'borehole')
        #todo restrict
      else:
        nuts.add(1, 'ocean')
        if self.veg == 'farm':
          nuts.add(2, 'kelp')
        if self.veg == 'fungus':
          nuts.cap(0, 'fungus')
    return nuts

  def mineral(self, base = None, faction = None):
    if base: faction = base.faction
    mins = DetailedValue(0)
    if self.base:
      mins.add(1, 'base square')
    else:
      if self.bonus == 'mineral':
        mins.add(2, 'bonus')
      if self.elev > 0:
        if self.veg == 'fungus':
          if self.improv == 'borehole':
            mins.add(6, 'borehole')
          else:
            mins.cap(0, 'fungus')
        elif self.veg == 'forest':
          mins.add(2, 'forest')
        else:
          if self.improv == 'borehole':
            mins.add(6, 'borehole')
          else:
            if self.rock:
              mins.add(1, 'rock/roll')
            if self.improv == 'mine':
              if self.rock == 2:
                mins.add(2, 'mine+rocky')
                if self.bonus == 'mineral':
                  mins.add(1, 'mine+rocky+bonus')
                if self.road:
                  mins.add(1, 'mine+rocky+road')
              else:
                mins.add(1, 'mine')
      else:
        if self.improv == 'platform':
          mins.add(1, 'platform')
        if self.veg == 'fungus':
          mins.cap(0, 'fungus')
    return mins

  def energy(self, base = None, faction = None):
    if base: faction = base.faction
    eng = DetailedValue(0)
    if self.base:
      eng.add(1, 'base square')
      #econo
    else:
      if self.bonus == 'energy':
        eng.add(2, 'bonus')
      if self.elev > 0:
        if self.veg == 'fungus':
          if self.improv == 'borehole':
            eng.add(6, 'borehole')
          else:
            eng.cap(0, 'fungus')
        elif self.veg == 'forest':
          eng.add(1, 'forest')
        else:
          if self.improv == 'collector':
            eng.add(((self.elev-1)/1000)+1, 'collector')
          if self.improv == 'borehole':
            eng.add(6, 'borehole')
      else:
        if self.improv == 'harness':
          eng.add(2, 'harness') 
        if self.veg == 'fungus':
          eng.cap(0, 'fungus')
      #econo
    return eng

class Node():
  def __init__(self, elev):
    self.elev = elev

base_coverage = [
   (-3, -1), (-2, -2), (-1, -3),
   (-3, 1), (-2, 0), (-1, -1), (0, -2), (1, -3),
   (-2, 2), (-1, 1), (1, -1), (2, -2),
   (-1, 3), (0, 2), (1, 1), (2, 0), (3, -1),
   (1, 3), (2, 2), (3, 1)]

class Base():
  def __init__(self, map, faction, pos, name):
    self.map = map
    self.faction = faction
    self.name = name
    self.pos = pos
    self.pop = 1#random.randint(1, 12)
    self.nuts = 0
    self.mins = 0
    self.facs = []
    self.worked_squares = []
    self.calc_citizens()

  @property
  def growth(self):
    gr = self.faction.growth.copy()
    #creche, golden age; vats?
    return gr

  def die(self):
    pass 

  def calc_citizens(self):
    self.talents = 0
    self.drones = 0
    self.specs = self.pop - self.drones - len(self.worked_squares)

  def turn(self):
    squares = [self.map.tsquare(pos) for pos in (self.worked_squares + [self.pos])]
    nuts = sum([sq.nutrient(self).val for sq in squares])
    self.nuts += nuts #- 2*self.pop
    if self.nuts < 0:
      self.nuts = 0
      self.pop -= 1
      if self.pop == 0:
        self.die()

    growth = self.faction.society('growth')
    grow_thres = (self.pop + 1) * (10 - growth.val)
    if self.nuts >= grow_thres:
      self.nuts -= grow_thres
      self.pop += 1 
      self.calc_citizens()
    #drones?
    #autoplace new workers

    mins = sum([sq.mineral(self).val for sq in squares])
    eng = sum([sq.energy(self).val for sq in squares])
    psych = (eng * self.faction.psych)/100
    econ = (eng * self.faction.econ)/100
    labs = (eng * self.faction.labs)/100
  
  def toggle_worker(self, pos):
    if pos in self.map.mcoor_lst(self.pos, base_coverage) and pos != self.pos:
      square = self.map.tsquare(pos)
      if pos not in self.worked_squares:
        if not square.base and not square.worked:
          if self.specs > 0:
            self.worked_squares.append(pos)
            square.worked = True
            self.specs -= 1
      else:
        self.worked_squares.remove(pos)
        square.worked = False
        self.specs += 1
           

class Faction():
  def __init__(self, state, key):
    self.state = state
    self.key = key
    self.energy = 0
    self.tech = []
    self.bases = []

    self.econ = 40
    self.psych = 30
    self.labs = 30

    self.politics = 'frontier'
    self.economics = 'simple'
    self.values = 'survival'
    self.future = 'none'

    self.models = {}
    self.models['politics'] = 'frontier'
    self.models['economics'] = 'simple'
    self.models['values'] = 'survival'
    self.models['future'] = 'none'

    self.basenames = copy.copy(self.state.rules.factions[self.key].basenames)

    self.new_base()

  def new_base(self):
    x, y = self.state.map.random()
    #base = Base(self.state.map, self, (x, y), "Base %d,%d" % (x, y))
    try:
      basename = self.basenames.pop()
    except IndexError: 
      basename = "Base %d" % len(self.bases)
    base = Base(self.state.map, self, (x, y), basename)
    self.state.map.squares[y][x].base = base
    self.bases.append(base)

  def get_se_soc(self, fkey):
    ret = []
    for key, model in self.models.iteritems():
      tech, lst = self.state.rules.models[model]
      for val, name in lst:
        if fkey == name:
          ret.append((val, model))
    return ret
  
  def get_faction_soc(self, fkey):
    ret = []
    for val, name in self.state.rules.factions[self.key].social:
      if fkey == name:
        ret.append((val, self.key)) 
    return ret

  def society(self, key):
    val = DetailedValue(0)
    for v, desc in (self.get_faction_soc(key) + self.get_se_soc(key)):
      val.add(v, desc)
    return val 

  def turn(self):
    for base in self.bases:
      base.turn()

  def __repr__(self):
    return self.key
    
class GameRoot():
  def __init__(self, arg = None):
    if arg:
      self.load(arg)
    else:
      self.new() 

  def load(self, fname = 'savegame'):
    with open(fname, 'rb') as f:
      data = f.read()
      self.state = pickle.loads(zlib.decompress(data))
      #self.state = pickle.load(f)

  def save(self, fname = 'savegame'):
    with open(fname, 'wb') as f:
      f.write(zlib.compress(pickle.dumps(self.state)))
      #pickle.dump(self.state, f)

  def new(self):
    self.state = GameState() 

  def turn(self):
    #multi 
    for i in range(len(self.state.factions)):
      self.state.end_turn()

faction_keys = ['gaians', 'hive', 'univ', 'morgan', 'spartans', 'believe', 'peace']

class GameState():
  def __init__(self):
    self.rules = rules.Rules(faction_keys)
    self.map = Map(20, 20)
    self.factions = [Faction(self, k) for k in faction_keys]
    self.fact_num = 0
    self.faction = self.factions[self.fact_num]
    #self.phase = 'move'
    self.year = 2100
  def end_turn(self):
    self.fact_num += 1
    if self.fact_num == len(self.factions):
      self.year += 1
      self.fact_num = 0
    self.faction = self.factions[self.fact_num]
    self.faction.turn() 

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

class MapWidget(Widget):
  expand = 1, 1
  ox, oy = 0, -2
  shrink = 0, 0
  #setsize = 1022, 700
  def init(self):
    self.m = 24
    self.focus = None
    self.fbase = None
    self.fsquare = None
    self.fcoords = None
    self.simple_elev = False
    self.setsize = None
    self.pos = 0, 0
    self.size = 0, 0
    self.texture = False
    self.elev_factor = 4000
    self.fnutrient = None
    self.fmineral = None
    self.fenergy = None
  #canvas or something
  def blit(self, img, pos):
    self.renderer.surface.blit(img, pos)

  def draw(self):
    images2 = img.get_images()
    m = self.m
    sx, sy = self.pos
    sw, sh = self.size
    w, h = (sw / (2*m)) +2, (sh / m) + 2
    clip = self.renderer.get_clip()
    self.renderer.set_clip(Rect(self.pos, self.size))
    def ltrb(x, y):
      l, t = sx + (x-1)*2*m, sy + (y-1)*m
      r, b =  sx + (x+1)*2*m, sy + (y+1)*m
      return l, t, r, b
    def cltrb(x, y):
      ct, cl = l + 2*m, t + m 
      cb, cr = l + 2*m, t + m
      return ct, cl, cb, cr
    def get_elev(x, y):
      if self.map.msquares(x, y):
        return self.map.msquares(x, y).elev
      return 0
    def offs(ex, ey):
      ot = (get_elev(ex, ey - 1)*m) /self.elev_factor
      ob = (get_elev(ex, ey + 1)*m) /self.elev_factor
      ocl = (get_elev(ex - 1, ey)*m) /self.elev_factor
      ocr = (get_elev(ex + 1, ey)*m) /self.elev_factor
      return ot, ob, ocl, ocr
    for y in range(h):
      for x in range(w): 
        if (x + y)%2 == 0:
          l, t, r, b = ltrb(x, y)
          ct, cl, cb, cr = cltrb(x, y)
          ex = x + self.ox
          ey = y + self.oy
          ot, ob, ocl, ocr = offs(ex, ey)           
          off = ot, ob, ocl, ocr
          t -= ot
          b -= ob
          cl -= ocl
          cr -= ocr
         
          square = self.map.msquares(ex, ey)
          if square:
            lev = int((square.elev+999)/1000)

            if self.simple_elev:
              t -= max(int((square.elev*m /self.elev_factor)), -0)
              self.renderer.naline(l, t+m, l+2*m, t+2*m, black)
              self.renderer.naline(r, t+m, l+2*m, t+2*m, black)
            
            if lev <= 0: 
              self.renderer.surface.blit(images2['ocean'](m), (l, t))  
              if square.veg == 'farm':
                self.blit(images2['kelp'](m), (l, b - 2*m))  
            else:
              n = ((ex % 5) + (ey % 7)) % 4
              if square.moist == 0: self.blit(images2['land'][n](m, off), (l, t + ot - 2*m))  
              elif square.moist == 1: self.blit(images2['moist'][n](m, off), (l, t + ot - 2*m))
              elif square.moist == 2: self.blit(images2['wet'][n](m, off), (l, t + ot - 2*m))
              if square.veg == 'farm':
                 if square.moist == 0: self.blit(images2['farmland1'](m, off), (l, t + ot - 2*m))  
                 elif square.moist > 0: self.blit(images2['farmland2'](m, off), (l, t + ot - 2*m))  
              elif square.veg == 'fungus':
                 self.blit(images2['fungus1'](m, off), (l, t + ot - 2*m))  
              elif square.veg == 'forest':
                 self.blit(images2['forest1'](m, off), (l, t + ot - 2*m))  

  
              if square.rock == 1: self.blit(images2['roll'][n](m, off), (l, t + ot - 2*m))  
              elif square.rock == 2: self.blit(images2['rock2'](m, off), (l, t + ot - 2*m))  
 
            #todo road 

            self.renderer.naline(l, cl, ct, t, landgrid)
            self.renderer.naline(r, cr, ct, t, landgrid)
            if not self.map.msquares(ex, ey + 1):
              self.renderer.naline(l, cl, cb, b, landgrid)
              self.renderer.naline(r, cr, cb, b, landgrid)
       
          if self.focus and self.fcoords == self.map.mapcoords(ex, ey):
            self.renderer.naline(l, cl, ct, t, red)
            self.renderer.naline(r, cr, ct, t, red)
            self.renderer.naline(l, cl, cb, b, red)
            self.renderer.naline(r, cr, cb, b, red)

 
          if square:
            if square.veg == 'farm' and square.elev > 0:
              f = (['farm1', 'farm2', 'farm3'][square.moist]            )
              self.blit(images2[f](m), (l, b - 2*m))  

            if square.bonus:
              if lev > 0:
                self.blit(images2[square.bonus](m), (l, b - 2*m))  
              else:
                self.blit(images2['w'+square.bonus](m), (l, b - 2*m))  

            if square.improv:  
              #self.renderer.surface.blit(images2[square.improv](m), (l, max(b - 2*m, cl - m, cr - m)))  
              self.renderer.surface.blit(images2[square.improv](m), (l, b - 2*m))  

    for y in range(h):
      for x in range(w): 
        if (x + y)%2 == 0:
          l, t, r, b = ltrb(x, y)
          ct, cl, cb, cr = cltrb(x, y)
          ex = x + self.ox
          ey = y + self.oy
          ot, ob, ocl, ocr = offs(ex, ey)           
          t -= ot
          b -= ob
          cl -= ocl
          cr -= ocr
          square = self.map.msquares(ex, ey)

          if square:
            lev = int((square.elev+999)/1000)
            if square.base:
              base = square.base 
              size = min(base.pop / 3, 3)
              if lev > 0:
                self.blit(images2[base.faction.key]['base'][size](m), (l, b - 2.75*m))  
              else:
                self.blit(images2[base.faction.key]['wbase'][size](m), (l, b - 2.75*m))  

           
            if self.fbase:
              if self.map.tmcoor((ex, ey)) in self.fbase.worked_squares + [self.fbase.pos]:
                square = self.map.msquares(ex, ey)
                nuts = square.nutrient(self.fbase).val
                mins = square.mineral(self.fbase).val
                eng = square.energy(self.fbase).val
                if nuts:
                  self.blit(images2['inutrient'][min(nuts, 8)], (l, t))
                if mins:
                  self.blit(images2['imineral'][min(mins, 8)], (l+m, t))
                if eng:
                  self.blit(images2['ienergy'][min(eng, 8)], (l+2*m, t))
                if nuts == 0 and mins == 0 and eng == 0:
                  self.blit(images2['inone'], (l+m, t))
        
            if square.base:
              base = square.base 
              w, h = self.renderer.font_size(base.name)
              self.renderer.font_render(base.name, images2[base.faction.key]['textcolor1'], (l+1+2*m-w/2, t+1+(m*1.8))) 
              self.renderer.font_render(base.name, images2[base.faction.key]['textcolor0'], (l+2*m-w/2, t+(m*1.8))) 
              backcolor = images2[base.faction.key]['color0']
              color = black
              print backcolor
              if backcolor == black: color = white #sparta kludge
              self.renderer.font_render(str(base.pop), color, (l, t-m), background = backcolor, bold = True) 
    
    self.renderer.set_clip(clip)

  def do(self, events):
    self.map = self.root.state.map
    self.events(events)

  def on_mousebutton(self, event):
    sx, sy = self.pos
    mx, my = event.pos
    mx, my = mx - sx, my - sy
    m = self.m
    k = (mx + my*2 + 2*m)/(4*m)
    l = (mx - my*2 + 2*m)/(4*m) 
    x, y = k+l, k-l
    ex, ey = x + self.ox, y + self.oy
    if self.map.msquares(ex, ey):
      ex, ey = self.map.tmcoor((ex, ey))
      if self.fbase and (ex, ey) in self.map.mcoor_lst(self.fbase.pos, base_coverage) and not self.map.tsquare((ex, ey)).base: 
          self.fbase.toggle_worker((ex, ey))
      else:
        self.focus = x, y
        self.fcoords = self.map.mapcoords(x + self.ox, y + self.oy)
        self.fsquare = self.map.msquares(x + self.ox, y + self.oy)
        if self.fsquare.base:# and not self.fbase: 
          self.fbase = self.fsquare.base
        else:
          self.fbase = None
      self.fnutrient = self.fsquare.nutrient().detail
      self.fmineral = self.fsquare.mineral().detail
      self.fenergy = self.fsquare.energy().detail
    #else:
    #  self.focus = None
    #  self.fcoords = None
    #  self.fsquare = None
 

def DGFrame(chl):
  return OPRFrame(child = OPRFrame(child = chl, fwidth = 2, color = green3), fwidth = 2, color = green2)

def HDGFrame(chl, label):
  vbox = VB([
    OPRFrame(child = HB([Label(text = label, color = baseheader, bold = True)]), fwidth = 2, color = green3), 
    Glue(setsize = (1, 1), expand = (0, 0)), 
    OPRFrame(child = chl, fwidth = 2, color = green3)
  ])
  return OPRFrame(child = vbox, fwidth = 3, color = green2)



class LoadLabel(Label): 
  def on_mousebutton(self, event): root.load()
class SaveLabel(Label): 
  def on_mousebutton(self, event): root.save()
class NewLabel(Label):
  def on_mousebutton(self, event): root.new()
class TurnLabel(Label):
  def on_mousebutton(self, event): root.turn()


def mglue(): return Glue(setsize = (10, 0), expand = (0, 0)) 

menu = HB([
  LoadLabel(text = 'Load', color = blue1), mglue(), 
  SaveLabel(text = 'Save', color = blue1), mglue(), 
  NewLabel(text = 'New', color = blue1), mglue(), 
  TurnLabel(text = 'End Turn', color = blue1), mglue(), 
  ])


root = GameRoot()

mapwidget = MapWidget(root = root)
fmap = OPFrame(child = mapwidget, fwidth = 1, color = green3)
rootview = Frame(fwidth = 2, child = HDGFrame(ObjView(ref = root, attr = 'state', color = green1, color2 = green2), 'STATE'))
sqview = Frame(fwidth = 2, child = HDGFrame(ObjView(ref = mapwidget, attr = 'fsquare', color = green1, color2 = green2), 'SQUARE'))
baseview = Frame(fwidth = 2, child = HDGFrame(ObjView(ref = mapwidget, attr = 'fbase', color = green1, color2 = green2), 'BASE'))
nutview = Frame(fwidth = 2, child = HDGFrame(ListView(ref = mapwidget, attr = 'fnutrient', color = green1, color2 = green2), 'NUTRIENT'))
minview = Frame(fwidth = 2, child = HDGFrame(ListView(ref = mapwidget, attr = 'fmineral', color = green1, color2 = green2), 'MINERAL'))
engview = Frame(fwidth = 2, child = HDGFrame(ListView(ref = mapwidget, attr = 'fenergy', color = green1, color2 = green2), 'ENERGY'))

panel = HB([rootview, sqview, baseview, nutview, minview, engview])
widgets = VB([menu, fmap, panel])
loop.main(widgets, img.init)
