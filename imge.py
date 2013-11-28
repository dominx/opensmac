import pygame.image
import pygame.transform
from pygame.rect import Rect

tst = 1

global images

images = None

def init():
  global images
  m = 25
  def getpic(surf, l, t, w, h):
    tmp = surf.subsurface(Rect(l, t, w, h)).copy()
    tmp.set_colorkey(255)
    return tmp.convert_alpha()

  def getisopic(surf, scale, l, t, w, h):
    tmp = getpic(surf, l, t, w, h)
    tmp = pygame.transform.rotate(tmp, 45)
    return pygame.transform.scale(tmp, (4*scale, 2*scale))
  
  texture = pygame.image.load('./pcx/texture.pcx') 
  land = getisopic(texture, m, 1, 58, 56, 56)
  moist1 = getisopic(texture, m, 1, 115, 56, 56)
  wet1 = getisopic(texture, m, 1, 343, 56, 56)
  moist = getisopic(texture, m, 1, 58, 56, 56)
  shelf = getisopic(texture, m, 280, 79, 56, 56)
  ocean = getisopic(texture, m, 280, 136, 56, 56)
  roll1 = getisopic(texture, m, 1, 1, 56, 56)
  rock1 = getisopic(texture, m, 58, 1, 56, 56)

  univ = pygame.image.load('./pcx/univ.pcx') 
  base = getpic(univ, 1, 1, 100, 75)
  base2 = getpic(univ, 304, 1, 100, 75)

  images = [land, shelf, ocean, base, roll1, rock1, moist1, wet1] 

def get_images():
  return images
