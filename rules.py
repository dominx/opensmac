import txt
import copy

def split_strip(line):
  return [f.strip() for f in line.split(',')]

class Technology():
  def __init__(self, name, key, values, preq1, preq2, flags):
    self.name = name
    self.key = key
    self.values = values
    self.preq1 = preq1
    self.preq2 = preq2
    self.flags = flags
    self.might = sum([int(v) for v in values])


class Facility():
  def __init__(self, name, key, cost, maint, preq, free_maint, effects, global_effects):

    def parse_effect(eff):
      e = split_strip(eff)  
      if e[0] == 'sp':
        self.sp = True
        return None
      elif e[0] == 'preq':
        self.preq_fac = e[1]
        return None
      elif len(e) == 1:
        return e[0], 'int', 1 
      elif len(e) == 2:
        try:
          return e[0], 'int', int(e[1])
        except ValueError:
          return e[0], 'str', e[1]
      elif len(e) == 3:
        try:
          return e[0], 'int_pair', (int(e[1]), int(e[2]))
        except ValueError:
          return e[0], 'str_pair', (e[1], e[2])
      print "At ", name ,"too many effect parameters:", e
      return "effect_error", 0

    self.name = name
    self.key = key
    self.cost = cost
    self.maint = maint
    self.preq = preq
    self.free_maint = free_maint
    self.sp = False
    self.preq_fac = None
    self.effects = [parse_effect(e) for e in effects if parse_effect(e)]
    self.global_effects = [parse_effect(e) for e in global_effects if parse_effect(e)]
  
def parse_soc(st):
  plus = len(st.split('+')) - 1
  minus = len(st.split('-')) - 1
  return plus - minus, st.strip('+-').lower()

class FactionRules():
  def __init__(self, fkey, data):
    #specials
    lines = data[fkey]
    rspec = split_strip(lines[1])
    special = zip(rspec[::2], rspec[1::2])
    #print [(k, v) for k, v in special if k != 'SOCIAL' and k != 'TECH']
    #print [(k, v) for k, v in special]
    self.social = [] 
    for name, val in special:
      if name == 'SOCIAL':
        self.social.append(parse_soc(val))
      if name == 'TECH' :
        pass 
    #basenames 
    lines = data['bases']
    self.basenames = copy.copy(lines)
    self.basenames.reverse() 

class Rules():
  def __init__(self, faction_keys):
    #technology
    self.tech = {}
    for line in txt.data.alphax.technology:
      d = split_strip(line)
      self.tech[d[1]] = Technology(d[0], d[1], (d[2], d[3], d[4], d[5]), d[6], d[7], d[8])

    #SOCIO
    self.models = {}
    for off in [3, 7, 11, 15]:
      for line in txt.data.alphax.socio[off:off+4]:
        f = split_strip(line)
        s = [parse_soc(e.strip()) for e in f[2:]]
        self.models[f[0].lower()] = f[1].strip(), s

    #factions
    self.factions = {}
    for fkey in faction_keys:
      self.factions[fkey] = FactionRules(fkey, txt.data2[fkey])
    
    #facilites & SPs
    self.facs = {}
    #deffs = []
    for aline, cline in zip(txt.data.alphax.facilities, txt.data.compat.facilities):
      a = split_strip(aline)
      c = split_strip(cline)
      key = c[1]
      effects = c[2:]
      try:
        i = effects.index('global')
        locs = effects[:i]
        globs = effects[i+1:]
      except ValueError:
        locs = effects
        globs = []
      #deffs += globs + locs
      if a[4] == 'Disable':
        a[4] = None
      if a[3] != 'Disable': 
        self.facs[key] = Facility(a[0], key, a[1], a[2], a[3], a[4], locs, globs)
        print a[0], key, a[1], a[2], a[3], a[4], locs, globs
    #print list(set(deffs))
