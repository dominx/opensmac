
import pygame, ctrl, render, widget

def main(widgets, init = lambda: 0):
  clock = pygame.time.Clock()
  get_events = ctrl.WidgetController()
  renderer = render.renderer((1024,768))
  #renderer = render.renderer(None)
  root = widget.RootWidget(renderer = renderer, child = widgets)
  init()
  loop = True
  while loop:
    
    loop = root.do(get_events())
    clock.tick(10)
    #raw_input()

