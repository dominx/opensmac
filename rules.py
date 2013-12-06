import txt
import copy

class Technology():
  def __init__(self, name, key, values, preq1, preq2, flags):
    self.name = name
    self.key = key
    self.values = values
    self.preq1 = preq1
    self.preq2 = preq2
    self.flags = flags
    self.might = sum([int(v) for v in values])

def split_strip(line):
  return [f.strip() for f in line.split(',')]

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
      d = line.split(',')
      self.tech[d[1]] = Technology(d[0], d[1], (d[2], d[3], d[4], d[5]), d[6], d[7], d[8])

    #SOCIO
    self.models = {}
    for off in [3, 7, 11, 15]:
      for line in txt.data.alphax.socio[off:off+4]:
        f = line.split(',')
        s = [parse_soc(e.strip()) for e in f[2:]]
        self.models[f[0].lower()] = f[1].strip(), s

    #factions
    self.factions = {}
    for fkey in faction_keys:
      self.factions[fkey] = FactionRules(fkey, txt.data2[fkey])
