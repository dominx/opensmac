import random
import copy
from pygame.rect import Rect
import cPickle as pickle
import zlib

from widget import *
import img
import loop
import rules
from square import Square, DetailedInt
from base import Base, base_coverage 
from faction import Faction      
from map import Map, Node

faction_keys = ['gaians', 'hive', 'univ', 'morgan', 'spartans', 'believe', 'peace']

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
    for f in range(len(self.state.factions)):
      self.state.end_turn()

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
              if backcolor == black: color = white #sparta kludge
              self.renderer.font_render(str(base.pop), color, (l, t-m), background = backcolor, bold = True) 
    
    self.renderer.set_clip(clip)

  def do(self, events):
    self.map = self.root.state.map
    return self.events(events)

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

class CitizenView(HBox):
  def do(self, events):
    base = getattr(self.ref, self.attr)
    if base:
      #print base.pop, base.specs, base.drones, base.superdrones, base.talents 
      workers = base.pop - base.specs - base.drones - base.superdrones - base.talents 
      lst = ['mtalent'] * base.talents + ['mworker'] * workers + ['mdrone'] * base.drones \
        + ['msuperdrone'] * base.superdrones + ['doctor'] * base.specs
      self.children = [Image(image = img.images[citizen]) for citizen in lst] 
      self.set_all(renderer = self.renderer)
    return events

root = GameRoot()

def mglue(): return Glue(setsize = (10, 0), expand = (0, 0)) 

def textover(otext, obj):
  return Stack(children = [obj, Label(color = red, text = otext)]) 

def stack(lst):
  return Stack(children = lst)

menu = HB([
  Label(text = 'Load', color = blue1, on_mousebutton = lambda e: root.load()), mglue(), 
  Label(text = 'Save', color = blue1, on_mousebutton = lambda e: root.save()), mglue(), 
  Label(text = 'New', color = blue1, on_mousebutton = lambda e: root.new()), mglue(), 
  Label(text = 'End Turn', color = blue1, on_mousebutton = lambda e: root.turn()), mglue(), 
  ])

mapwidget = MapWidget(root = root)
fmap = OPFrame(
  child = mapwidget, 
  fwidth = 1, 
  color = green3)

rootview = Frame(fwidth = 2, child = HDGFrame(ObjView(ref = root, attr = 'state', color = green1, color2 = green2), 'STATE'))
sqview = Frame(fwidth = 2, child = HDGFrame(ObjView(ref = mapwidget, attr = 'fsquare', color = green1, color2 = green2), 'SQUARE'))
baseview = Frame(fwidth = 2, child = HDGFrame(bground(ObjView(ref = mapwidget, attr = 'fbase', color = green1, color2 = green2)), 'BASE'))
baseview2 = Frame(fwidth = 2, child = HDGFrame(bground(ObjView(ref = mapwidget, attr = 'fbase', color = green1, color2 = green2)), 'BASE'))
nutview = Frame(fwidth = 2, child = HDGFrame(ListView(ref = mapwidget, attr = 'fnutrient', color = green1, color2 = green2), 'NUTRIENT'))
minview = Frame(fwidth = 2, child = HDGFrame(ListView(ref = mapwidget, attr = 'fmineral', color = green1, color2 = green2), 'MINERAL'))
engview = Frame(fwidth = 2, child = HDGFrame(ListView(ref = mapwidget, attr = 'fenergy', color = green1, color2 = green2), 'ENERGY'))
citizenview = Frame(fwidth = 2, child = DGFrame(CitizenView(ref = mapwidget,  attr = 'fbase')))

fmap = stack([fmap, PosBox(childpossizes = [(baseview2, (100, 100), (100, 100))])])

panel2 = VB([nutview, minview, engview])
panel = HB([rootview, sqview, baseview, citizenview, panel2])
#panel = HB([rootview, sqview, citizenview, panel2])
#panel = HB([rootview, sqview, baseview])
widgets = VB([menu, fmap, panel])
#widgets = VB([menu, stack([fmap, panel])])
loop.main(widgets, img.init)
