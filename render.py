import pygame
import pygame.gfxdraw
import pygame.font



class GDRenderer: 
  fontclip = 2
  def __init__(self, surface, font, offset = (0, 0)):
    self.surface = surface
    self.font = font
    self.ox, self.oy = offset
  def sub(self, offset):
    ox, oy = offset
    return GDRenderer(self.surface, self.font, (self.ox + ox, self.oy + oy))
  def circle(self, x, y, r, color):
    x, y = x + self.ox, y + self.oy
    pygame.gfxdraw.aacircle(self.surface, int(x), int(y), int(r), color)
  def fcircle(self, x, y, r, color):
    x, y = x + self.ox, y + self.oy
    pygame.gfxdraw.aacircle(self.surface, int(x), int(y), int(r), color)
    pygame.gfxdraw.filled_circle(self.surface, int(x), int(y), int(r), color)
  def line(self, x1, y1, x2, y2, color):
    p1 = x1 + self.ox, y1 + self.oy
    p2 = x2 + self.ox, y2 + self.oy
    pygame.gfxdraw.aapolygon(self.surface, [p1, p2, p1], color)
  def naline(self, x1, y1, x2, y2, color):
    pygame.gfxdraw.line(self.surface, x1 + self.ox, y1 + self.oy, x2 + self.ox, y2 + self.oy, color)
  def hline(self, x1, x2, y, color):
    pygame.gfxdraw.hline(self.surface, x1 + self.ox, x2 + self.ox, y + self.oy, color)
  def vline(self, x, y1, y2, color):
    pygame.gfxdraw.vline(self.surface, x + self.ox, y1 + self.oy, y2 + self.oy, color)
  def poly(self, lst, color):
    plst = []
    for x, y in lst:
      plst.append((x + self.ox, y + self.oy))
    pygame.gfxdraw.aapolygon(self.surface, plst, color)
  def fpoly(self, lst, color):
    plst = []
    for x, y in lst:
      plst.append((x + self.ox, y + self.oy))
    pygame.gfxdraw.filled_polygon(self.surface, plst, color)
  def nonaapoly(self, lst, color):
    plst = []
    for x, y in lst:
      plst.append((x + self.ox, y + self.oy))
    pygame.gfxdraw.polygon(self.surface, plst, color)
  def rect(self, x1, y1, x2, y2, color):
    self.poly([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], color)     
  def frect(self, x1, y1, x2, y2, color):
    self.fpoly([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], color)     
  def clear(self):
    self.surface.fill((0, 0, 0))
  def get_size(self):
    return self.surface.get_size()
  def set_font_attr(self, bold):
    if bold:
      self.font.set_bold(True)
    else:
      self.font.set_bold(False)
 
  def font_size(self, text, bold = False):
    self.set_font_attr(bold)
    w, h = self.font.size(text)
    return w, h - self.fontclip
  def font_render(self, text, color, (x, y), (w, h), background = None, bold = False):
    self.set_font_attr(bold)
    if background:
      image = self.font.render(text, False, color, background)
    else:
      image = self.font.render(text, False, color)
    clip = image.get_rect()
    clip.top = self.fontclip
    clip.height -= self.fontclip
    if clip.height > h: clip.height = h
    if clip.width > w: clip.height = w
    return self.surface.blit(image, (x + self.ox, y + self.oy), clip)
  def set_clip(self, rect = None):
    self.surface.set_clip(rect)
  def get_clip(self):
    return self.surface.get_clip()

def renderer(size):
  pygame.font.init()
  #font = pygame.font.SysFont('arial', 10)
  font = pygame.font.Font('arialn.ttf', 14)
  pygame.display.init() 
  pygame.display.set_caption('opensmac')
  if size:
    screen = pygame.display.set_mode(size)
  else:
    screen = pygame.display.set_mode(pygame.display.list_modes()[0], pygame.FULLSCREEN)
  return GDRenderer(screen, font)

def flip():
  pygame.display.flip()
