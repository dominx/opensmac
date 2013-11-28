
import pygame
from pygame.locals import *
import sys
import random


key_bindings = {
  K_o : "u", K_SEMICOLON : "r", K_l : "d", K_k : "l", 
  #K_h : "l", K_j : "d", K_k : "u", K_l: "r", 
  K_d : "a", K_s : "b", K_a : "c",
  K_e : "e", K_w : "f", K_q : "g",
  K_3 : "h", K_2 : "i", K_1 : "j",
  K_SPACE : "spc", K_ESCAPE : "esc",
}

white = 255, 255, 255
red = (255, 0, 0)
magenta = (255, 0, 255)

from pygame.color import THECOLORS

def rnd_color():
  name = random.choice(THECOLORS.keys())
  print 'rnd_color:', name
  return THECOLORS[name][:3]

globals().update(THECOLORS)


combos = '''
  RU=(ru):ur UR=(ru):ur
  UL=(lu):ul LU=(lu):ul
  LD=(ld):dl DL=(dl):dl
  DR=(rd):dr RD=(rd):dr 
  L=(lUD):l R=(rUD):r U=(uLR):u D=(dLR):d 
 
  LlL:tl RrR:tr UuU:tu DdD:td

  A:sh
  '''

combo_tmp = '''
  L=l:l R=r:r U=u:u D=d:d 
  DR=(dr):dr RD=(dr):rd
  RU=(ru):ru UR=(ru):ur
  UL=(lu):ul LU=(lu):lu
  LD=(ld):ld DL=(dl):dl

  '''

combos12 = '''
  DR=(rD):dr RD=(dR):rd
  RU=(uR):ru UR=(rU):ur
  UL=(lU):ul LU=(uL):lu
  LD=(dL):ld DL=(lD):dl
  L=(lUD):l R=(rUD):r U=(uRL):u D=(dRL):d 

  A:sh
  '''


def event_poll():
  keys = []
  for event in pygame.event.get():
    if event.type == QUIT: pygame.quit(); sys.exit()
    elif event.type == pygame.KEYDOWN:
      try: keys.append((key_bindings[event.key]).upper()) 
      except KeyError : pass 
    elif event.type == pygame.KEYUP:
      try: keys.append(key_bindings[event.key].lower()) 
      except KeyError : pass 
    #print event
  #if keys != []: print keys
  return keys



class Automaton:
  def __init__(self, expr):
    self.combo = self.parse(expr)
    self.reset()
    self.timeout = 20
  def reset(self):
    self.state = 0
    self.timer = 0
  def parse(self, expr):
    combo = []
    keys, sust, timeout = [], False, True
    p = 0
    while p < len(expr):
      if expr[p] == " ":
        pass
      elif expr[p] == "(":
        combo.append((keys, sust))
        keys, sust, timeout = [], False, True
        p += 1
        while expr[p] != ")":
          keys.append(expr[p])
          p += 1
      elif expr[p] == "=":
        sust = True
      elif expr[p] == "-":
        timeout = False
      else:
        combo.append((keys, sust, timeout))
        keys, sust, timeout = [], False, True
        keys.append(expr[p])
      p += 1
    combo.append((keys, sust, timeout))
    combo.pop(0)
    #print combo
    return combo
  def input(self, val):
    if val in self.combo[self.state][0]:
      self.state += 1
    else:
      if self.state > 0:
        if self.combo[self.state - 1][1]:
          return True
        else:
          if self.combo[self.state - 1][2]:
            self.timer += 1
            if self.timer == self.timeout:
              self.reset()
      return False
    if self.state == len(self.combo):
       self.reset()
       return True
    else:
       return False
    assert(False)

class Controler:
  def __init__(self, conf):
    lst = map(lambda s: tuple(s.split(":")),conf.split())
    self.auta = []
    for combo, command in lst:
      self.auta.append((Automaton(combo), command))
  def input(self, keys):
    commands = []
    keys.append("#")
    for key in keys:
      for auton, command in self.auta:
        if auton.input(key):
          commands.insert(0, command)
    #if commands != []: print commands
    return commands 

class S8Controler:
  def __init__(self):
    self.state = {}
    for i in "udlrabcefghij":
      self.state[i] = False
  def input(self, keys):
    com = ""
    for k in keys:
      for i in "udlrabcefghij":
        if k == i:
          self.state[i] = False
        elif k == i.upper():
          self.state[i] = True
    for i in "udlr":
        if self.state[i]: 
          com += i
    commands = [com]
    for i in "abcefghij":
        if self.state[i]:
          commands.append(i)
    for k in keys:
      if k in "abcefghij": 
        commands.append(k.upper())
      if k in  ['esc', 'spc']:
        commands.append(k)
    return commands
  def __call__(self):
    return self.input(event_poll())

class WidgetController():
  def __init__(self):
    pass
  def input(self, keys):
    return keys
  def __call__(self):
    events = pygame.event.get()
    for event in events:
      if event.type == QUIT: 
        pygame.quit(); sys.exit()
      if event.type == pygame.KEYDOWN:
        if event.key == K_ESCAPE:
          pygame.quit(); sys.exit()
    return events




