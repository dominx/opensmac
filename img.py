import os
import pygame.image
import pygame
import pygame.transform
from pygame.rect import Rect

shadowmask = (253, 189, 118)

pcx_dir = 'pcx'

def pic(surf, rect, colorkey = 255, colorkey2 = None):
  tmp = surf.subsurface(Rect(rect)).copy()
  tmp.set_colorkey(colorkey)
  if colorkey2:
    pygame.PixelArray(tmp).replace(colorkey2, colorkey)
  tmp = tmp.convert_alpha()
  pygame.PixelArray(tmp).replace(shadowmask, (0,0,0,128))
  return tmp

def rotpic(surf, (l, t, w, h), a = 45):
  tmp = pic(surf, (l, t, w, h))
  return pygame.transform.rotate(tmp, a)
  #return pygame.transform.scale2x(pygame.transform.rotate(tmp, a))

def rotlist(surf, rect, a = 45):
  return [rotpic(surf, rect, a = a+90*i) for i in range(4)]
  #return [CachedTexture(p) for p in lst]

class ScaledImage():
  def __init__(self, source, hscale = 4, vscale = 2):
    self.vscale = vscale
    self.hscale = hscale
    self.images = {}
    self.source = source
  def __call__(self, scale):
    if scale in self.images:
      return self.images[scale]
    else:
      self.images[scale] = pygame.transform.scale(self.source, (int(self.hscale*scale), int(self.vscale*scale)))
      return self.images[scale]

       
class CachedTexture(ScaledImage):
  def __call__(self, scale, offs = (0, 0, 0, 0)):
    if (scale, offs) in self.images.keys():
      return self.images[scale, offs]
    else:
      if sum(offs) > 0:
        ot, ob, ocl, ocr = offs 
        img = pygame.Surface((4*scale, 4*scale), flags = pygame.SRCALPHA)

        tl = self(scale).subsurface(pygame.Rect(0 , 2*scale, 2*scale, scale))
        tl = pygame.transform.scale(tl, (2*scale, scale + ot - ocl))
        img.blit(tl, (0, 2*scale - ot))

        tl = self(scale).subsurface(pygame.Rect(2*scale , 2*scale, 2*scale, scale))
        tl = pygame.transform.scale(tl, (2*scale, scale + ot - ocr))
        img.blit(tl, (2*scale, 2*scale - ot))

        tl = self(scale).subsurface(pygame.Rect(0 , 3*scale, 2*scale, scale))
        tl = pygame.transform.scale(tl, (2*scale, scale - ob + ocl))
        img.blit(tl, (0, 3*scale - ocl))

        tl = self(scale).subsurface(pygame.Rect(2*scale , 3*scale, 2*scale, scale))
        tl = pygame.transform.scale(tl, (2*scale, scale - ob + ocr))
        img.blit(tl, (2*scale, 3*scale - ocr))

        self.images[(scale, offs)] = img 
      else:
        img = pygame.Surface((4*scale, 4*scale), flags = pygame.SRCALPHA)
        #img.blit(srpic(self.source, scale, self.geo), (0, 2*scale))
        img.blit(pygame.transform.scale(self.source, (4*scale, 2*scale)), (0, 2*scale))
        self.images[(scale, (0,0,0,0))] = img
      return self.images[scale, offs]
  

global images
images = None

def init():
  global images
 
  texture = pygame.image.load(os.path.join(pcx_dir,'texture.pcx')) 
  ter1 = pygame.image.load(os.path.join(pcx_dir,'ter1.pcx')) 
  newicons = pygame.image.load(os.path.join(pcx_dir,'newicons.pcx')) 

  def faction(name):
    img = pygame.image.load(os.path.join(pcx_dir, '%s.pcx' % name))
    return {
      'base' : [ScaledImage(pic(img, (x, 1, 100, 75)), vscale = 3) for x in [1, 102, 203, 304]],
      'wbase' : [ScaledImage(pic(img, (x, 229, 100, 75)), vscale = 3) for x in [1, 102, 203, 304]],
    }
    
  #shelf = getisopic(texture, m, 280, 79, 56, 56)
  #land = [rotpic(texture, (1, 58, 56, 56), a = 45+90*i) for i in range(4)]
  #land = [CachedTexture(p) for p in land]

  land = [CachedTexture(p) for p in rotlist(texture, (1, 58, 56, 56))]
  moist = [CachedTexture(p) for p in rotlist(texture, (1, 115, 56, 56))]
  wet = [CachedTexture(p) for p in rotlist(texture, (1, 343, 56, 56))]
  roll = [CachedTexture(p) for p in rotlist(texture, (1, 1, 56, 56))]
  rock = [CachedTexture(p) for p in rotlist(texture, (58, 1, 56, 56))]
  faction_keys = ['gaians', 'hive', 'univ', 'morgan', 'spartans', 'believe', 'peace',
    'cyborg', 'pirates', 'drone', 'angels', 'fungboy']
  faction_images = {k : faction(k) for k in faction_keys}
  images = {
    #'univ' : faction('univ'),
    'land' : land,
    'moist' : moist,
    'wet' : wet,
    'roll' : roll,
    'rock' : rock,
    'land1' :  CachedTexture(rotpic(texture, (1, 58, 56, 56))),
    'moist1' : CachedTexture(rotpic(texture, (1, 115, 56, 56))),
    'wet1' :  CachedTexture(rotpic(texture, (1, 343, 56, 56))),
    'roll1' :  CachedTexture(rotpic(texture, (1, 1, 56, 56))),
    'rock1' :  CachedTexture(rotpic(texture, (58, 1, 56, 56))),
    'rock2' :  CachedTexture(rotpic(texture, (172, 1, 56, 56))),
    'farmland1' : CachedTexture(rotpic(texture, (775, 219, 56, 56))),
    'farmland2' : CachedTexture(rotpic(texture, (832, 219, 56, 56))),
    'fungus1' : CachedTexture(rotpic(texture, (280, 516, 56, 56))),
    'forest1' : CachedTexture(rotpic(texture, (526, 6, 56, 56))),

    #'base1' : ScaledImage(pic(univ, (1, 1, 100, 75)), vscale = 3),
    #'base2' : ScaledImage(pic(univ, (304, 1, 100, 75)), vscale = 3),
    #improvs
    'farm1' : ScaledImage(pic(ter1, (923, 453, 100, 62), 253, 252), vscale = 2.5),
    'farm2' : ScaledImage(pic(ter1, (923, 516, 100, 62), 253, 252), vscale = 2.5),
    'farm3' : ScaledImage(pic(ter1, (923, 579, 100, 62), 253, 252), vscale = 2.5),
    'farm4' : ScaledImage(pic(ter1, (923, 642, 100, 62), 253, 252), vscale = 2.5),

    'kelp' : ScaledImage(pic(ter1, (607, 190, 100, 62), 253, 252), vscale = 2.5),

    'monolith' : ScaledImage(pic(ter1, (304, 1, 100, 62), 253, 252), vscale = 2.5),
    'platform' : ScaledImage(pic(ter1, (506, 64, 100, 62), 253, 252), vscale = 2.5),
    'mine' : ScaledImage(pic(ter1, (607, 64, 100, 62), 253, 252), vscale = 2.5),
    'harness' : ScaledImage(pic(ter1, (506, 127, 100, 62), 253, 252), vscale = 2.5),
    'collector' : ScaledImage(pic(ter1, (607, 127, 100, 62), 253, 252), vscale = 2.5),
    'condenser' : ScaledImage(pic(ter1, (506, 253, 100, 62), 253, 252), vscale = 2.5),
    'mirror' : ScaledImage(pic(ter1, (607, 253, 100, 62), 253, 252), vscale = 2.5),
    'aborehole' : ScaledImage(pic(ter1, (708, 190, 100, 62), 253, 252), vscale = 2.5),
    'borehole' : ScaledImage(pic(ter1, (708, 253, 100, 62), 253, 252), vscale = 2.5),
    'bunker' : ScaledImage(pic(ter1, (506, 316, 100, 62), 253, 252), vscale = 2.5),
    'airbase' : ScaledImage(pic(ter1, (607, 316, 100, 62), 253, 252), vscale = 2.5),
    'sensor' : ScaledImage(pic(ter1, (708, 316, 100, 62), 253, 252), vscale = 2.5),
    #bonus
    'nutrient' : ScaledImage(pic(ter1, (203, 253, 100, 62), 253, 252), vscale = 2.5),
    'mineral' : ScaledImage(pic(ter1, (203, 316, 100, 62), 253, 252), vscale = 2.5),
    'energy' : ScaledImage(pic(ter1, (203, 379, 100, 62), 253, 252), vscale = 2.5),
    'wnutrient' : ScaledImage(pic(ter1, (1, 253, 100, 62), 253, 252), vscale = 2.5),
    'wmineral' : ScaledImage(pic(ter1, (1, 316, 100, 62), 253, 252), vscale = 2.5),
    'wenergy' : ScaledImage(pic(ter1, (1, 379, 100, 62), 253, 252), vscale = 2.5),

    'ocean' : ScaledImage(rotpic(texture, (280, 136, 56, 56))),
    'inutrient' : { n :pic(newicons, (174 + (n-1)*41, 304, 40, 40)) for n in range(1, 9)},
    'imineral' : { n :pic(newicons, (174 + (n-1)*41, 345, 40, 40)) for n in range(1, 9)},
    'ienergy' : { n :pic(newicons, (174 + (n-1)*41, 386, 40, 40)) for n in range(1, 9)},
    'inone': pic(newicons, (1, 174, 22, 22)),
  }
  images.update(faction_images)

def get_images():
  return images
