
import pygame, ctrl, render, widget, img 

import interface

import cProfile

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
    #events = get_events()
    #if events:
    #  loop = root.do(events)
    clock.tick(10)
    #raw_input()

#cProfile.run("loop.main(widgets, img.init)", sort = 'time')
main(interface.widgets, img.init)
