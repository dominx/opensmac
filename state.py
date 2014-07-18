import random
import copy
import cPickle as pickle
import zlib

import rules
from faction import Faction      
from map import Map

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


root = GameRoot()

