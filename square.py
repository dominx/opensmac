
from detailed import DetailedInt

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
    nuts = DetailedInt()
    if self.base:
      #todo reference rules
      #nuts.add(2, 'base square')
      nuts += 2, 'base square'
      nuts += self.base.effect('base_nut')
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
          if nuts.val > 0:
            nuts.add(-1, 'mine')
          #nuts.lcap(0, '')
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
    mins = DetailedInt()
    if self.base:
      mins.add(1, 'base square')
      #nuts.add(self.base.effect('base_nut').val, self.base.effect('base_nut').desc)
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
    eng = DetailedInt(0)
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


