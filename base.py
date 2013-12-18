
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
    talents += self.psych()/2
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    #facs
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    #police
    talents, drones, superdrones = reduce(talents, drones, superdrones)
    #sp
    talents, drones, superdrones = reduce(talents, drones, superdrones)
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
    return soc

  def psych(self):
    psych = (self.energy() * self.faction.psych)/100
    psych += 2 * self.specs
    # % bonus
    return psych 

  def econ(self):
    econ = (self.energy() * self.faction.econ)/100
    #specs
    # % fac bonus
    return econ 

  def labs(self):
    labs = (self.energy() * self.faction.labs)/100
    #specs
    # % fac bonus
    return labs

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
      self.pop -= 1
      if self.pop == 0:
        self.die()
    else:
      growth = self.society('growth')
      grow_thres = (self.pop + 1) * (10 - min(growth.val, 5))
      if growth.val >= 6 and self.dnuts >= 2:
        #popboom
        self.pop += 1
        self.specs += 1
        #self.autoplace_workers
      else:
        #normal growth
        if self.nuts > grow_thres:
          self.nuts -= grow_thres
          self.pop += 1 
          self.specs += 1
          #self.autoplace_workers

    #energy
    #self.faction.add_labs(self.labs())
    #self.faction.energy += self.energy() - self.maintenance()
    #todo short maintenance

    #drone
    self.riot = self.calc_happyness()
    #autoplace new workers

    #self.d = nuts, mins, eng
    #self.ea = psych, econ, labs
    #self.eb = 2 * self.specs
 

  def toggle_worker(self, pos):
    if pos in self.map.mcoor_lst(self.pos, base_coverage) and pos != self.pos:
      square = self.map.tsquare(pos)
      if pos not in self.worked_squares:
        if not square.base and not square.worked:
          if self.specs > 0:
            self.worked_squares.append(pos)
            square.worked = True
            self.specs -= 1
            self.calc_happyness()
      else:
        self.worked_squares.remove(pos)
        square.worked = False
        self.specs += 1
        self.calc_happyness()
 
