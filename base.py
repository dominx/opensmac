
from detailed import DetailedInt

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
    self.queue = []
    self.facs = []
    self.worked_squares = []
    self.specs = self.pop
    self.drones = 0
    self.superdrones = 0
    self.riot = False
    self.calc_effects()
    self.calc_happyness()
    #self.autoplace_workers
    
  def die(self):
    pass 

  def calc_happyness(self):
    detail = []
    def reduce(talents, drones, superdrones):
      talents = min(all_workers, talents)
      while talents > 0 and (drones > 0  or superdrones > 0) and talents + drones + superdrones > all_workers:
        if superdrones > 0:
          talents -= 1
          superdrones -= 1
          drones += 1
        elif drones > 0:
          talents -= 1
          drones -= 1
      return talents, drones, superdrones
    def pacify(val):
      while val > 0:
        if drones:
          drones -= 1
        elif superdrones:
          superdrones -= 1
        val -= 1

    all_workers = self.pop - self.specs
    talents = 0 #+lal
    drones = max(0, all_workers - 1) # +zak, bureau, diff
    superdrones = 0
    if drones > all_workers:
      superdrones = max(drones - all_workers, all_workers)
      drones = all_workers - superdrones
    
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    talents += int(self.psych()/2)
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    drones -= self.effect('undrone').val
    drones += self.effect('drone').val
    talents += self.effect('talent').val
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    #police
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    #sp
    drones -= self.effect('undrone_sp').val
    drones += self.effect('drone_sp').val
    talents += self.effect('talent_sp').val
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    if self.effect('nodrone').val:
      drones = 0
    if self.effect('notalent').val:
      talents = 0
    self.drones = drones
    self.talents = talents
    self.superdrones = superdrones
    return drones + superdrones > talents

  def nutrient(self):
    squares = [self.map.tsquare(pos) for pos in (self.worked_squares + [self.pos])]
    nuts = sum([sq.nutrient(self).val for sq in squares])
    return nuts

  def mineral(self):
    squares = [self.map.tsquare(pos) for pos in (self.worked_squares + [self.pos])]
    mins = sum([sq.mineral(self).val for sq in squares])
    #bonus effects
    mins += mins * self.effect('mins').val
    return mins
 
  def energy(self):
    squares = [self.map.tsquare(pos) for pos in (self.worked_squares + [self.pos])]
    eng = sum([sq.energy(self).val for sq in squares])
    #ineffficeincy??
    #eng -= eng * (hqdist / 8(4 - effic))
    return eng

  def society(self, key):
    soc = self.faction.society(key).copy()
    #base soc effects
    if self.effect(key):
      soc += self.effect(key)
    return soc

  def psych(self):
    psych = (self.energy() * self.faction.psych)/100
    psych += 2 * self.specs
    bonus = self.effect('psych')
    if bonus:
      psych += psych * 0.5 * bonus.val
    bonus = self.effect('psych25')
    if bonus:
      psych += psych * 0.25 * bonus.val
    return psych 

  def econ(self):
    econ = (self.energy() * self.faction.econ)/100
    #specs
    # % fac bonus
    bonus = self.effect('econ')
    if bonus:
      econ += econ * 0.5 * bonus.val
    return econ 

  def labs(self):
    labs = (self.energy() * self.faction.labs)/100
    #specs
    bonus = self.effect('labs')
    if bonus:
      labs += labs * 0.5 * bonus.val
    if self.effect('halftech'):
      labs -= labs * 0.5
    return labs

  def local_effects(self):
    local = []
    for fkey in self.facs:
      local += [(eff, typ, val, fkey) for eff, val in self.faction.state.rules.facs[fac].effects]
    return local     
 
  def global_effects(self):
    glob = []
    for fkey in self.facs:
      glob += [(eff, typ, val, (fkey, self.name)) for eff, val in self.faction.state.rules.facs[fac].global_effects]
    return glob

  def calc_effects(self):
    raw_effects = self.local_effects() + self.faction.global_effects()
    effects = {}
    for eff, typ, val, source in raw_effects:
      if typ == 'int': 
        effects.setdefault(eff, DetailedInt(0)).add(val, source)
      else:
        effects.setdefault(eff, []).append((val, source)) 
    self.effects = effects

  def effect(self, eff, default = DetailedInt()):
    try:
      return self.effects[eff]
    except KeyError:
      return default

  def buildable_facs(self):
    facs = self.faction.state.rules.facs.values()
    facs = [fac for fac in facs if fac.preq in self.faction.tech or fac.preq == 'None']
    facs = [fac for fac in facs if fac.preq_fac and fac.preq_fac in self.facs]
    return [fac for fac in facs if fac.key not in self.facs]      

  def turn(self):
    #famine check
    dnuts = self.nutrient() - 2*self.pop
    print self.nuts, dnuts
    self.nuts += dnuts 
    if self.nuts < 0:
      self.nuts = 0
      self.famine = True
    else:
      self.famine = False

    #build
    dmin = self.mineral()
    # if dmin < 0: short support
    self.mins += dmin
    if self.queue:
      if self.mins >= self.queue[0].cost:
        if not self.famine and not self.riot:
          self.mins -= self.queue[0].cost
          obj = self.queue.pop(0)
          self.build(obj)
    else:
      #stockpile
      self.faction.energy += self.mins / 2
      self.mins = 0

    #growth
    if self.famine: 
      self.shrink()
    else:
      growth = self.society('growth')
      grow_thres = (self.pop + 1) * (10 - min(growth.val, 5))
      if growth.val >= 6 and self.dnuts >= 2:
        #popboom
        self.grow()
      else:
        #normal growth
        if self.nuts > grow_thres:
          self.nuts -= grow_thres
          self.grow()

    #energy
    #self.faction.add_labs(self.labs())
    #self.faction.energy += self.energy() - self.maintenance()
    #todo short maintenance

    #drone
    self.riot = self.calc_happyness()
    #autoplace new workers

    #debug
    #self.d = nuts, mins, eng
    #self.ea = psych, econ, labs
    #self.eb = 2 * self.specs
    self.bf = [fac.key for fac in self.buildable_facs()]   

  def grow(self):
    self.pop += 1
    self.add_spec()
    #self.autoplace_workers

  def shrink(self):
      self.pop -= 1
      #remove worker or spec!
      if self.specs:
        self.rem_spec()
      else:
        self.rem_worker()
      if self.pop == 0:
        self.die()

  def add_spec(self):
    self.specs += 1

  def rem_spec(self):
    self.specs -= 1

  def rem_worker(self):
    pos = self.worked_squares.pop()
    self.map.tsquare(pos).worked = False

  def toggle_worker(self, pos):
    if pos in self.map.mcoor_lst(self.pos, base_coverage) and pos != self.pos:
      square = self.map.tsquare(pos)
      if pos not in self.worked_squares:
        if not square.base and not square.worked:
          if self.specs > 0:
            self.worked_squares.append(pos)
            square.worked = True
            self.rem_spec()
            self.calc_happyness()
      else:
        self.worked_squares.remove(pos)
        square.worked = False
        self.add_spec()
        self.calc_happyness()
 
