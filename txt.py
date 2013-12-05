


import os

txt_dir = 'txt'

def filenames(dir):
  for dirname, dirnames, filenames in os.walk(dir):
    if dirname == dir:
      filenames = [name for name in filenames if name.split('.')[1] == 'txt']
      return zip([os.path.join(dirname, filename) for filename in filenames], filenames)

def cleanlines(lines):
  lines = [line.split(';')[0].strip().strip(',') for line in lines]
  lines = filter(lambda l: l != "", lines)
  return lines

def filelines():
  retlines = []
  for pathname, name in filenames(txt_dir):
    with open(pathname) as f:
      lines = cleanlines(f.readlines())
      name = name.split('.')[0].lower()
      retlines.append((name, lines))
  return retlines


def shfileparse(lines):
    sections = []
    key = None
    items = []
    for line in lines:
      if line[0] == '#':
        if len(line) > 1:
          if line[1] != '#':  #ugly hack for alphax.txt hashed section or are ## lines ignored by orginal parser?
            if key:
              if not key[0] == ' ': # hack for note for translator in alpha.txt
                sections.append((key, items))
              items = []
            key = line[1:].lower()
          else: # '##' lines
            pass
      else: 
        items.append(line)
    return sections

class SugarDict:
  def __init__(self, lst):
    for key, value in lst:
      setattr(self, key.lower(), value)
    setattr(self, 'rawdata', lst)

#def do(): pass 
#do()

rawfiles = filelines()
#shfiles =  [(k, v) for k, v in files if v[0][0] == '#' and v[0][1] != '#'] #single hash files 
#dhfiles =  [(k, v) for k, v in files if v[0][0] == '#' and v[0][1] == '#' and v[0] != '##'] #double hash files
#xsfiles =  [(k, v) for k, v in shfiles if len(v[1])> 1 and v[1][0] == '#' and v[1][1] == 'x'] 
#shfiles =  [(k, v) for k, v in shfiles if len(v[1])<=1 or (len(v[1])> 1 and (v[1][0] != '#' or v[1][1] != 'x'))] #xs turns up later in the files

parsedfiles = [(f, SugarDict(shfileparse(lines))) for f, lines in rawfiles]
data = SugarDict(parsedfiles)

data2 = { f : dict(shfileparse(lines)) for f, lines in rawfiles}

#for i in data.alphax.citizens:
#  print i
