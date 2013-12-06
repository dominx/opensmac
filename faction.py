import copy
from base import Base

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
    

