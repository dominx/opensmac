
import pygame
from pygame.locals import *
import sys
import random

def event_poll():
  keys = []
  for event in pygame.event.get():
    if event.type == QUIT: pygame.quit(); sys.exit()
    elif event.type == pygame.KEYDOWN:
      try: keys.append((key_bindings[event.key]).upper()) 
      except KeyError : pass 
    elif event.type == pygame.KEYUP:
      try: keys.append(key_bindings[event.key].lower()) 
      except KeyError : pass 
    #print event
  #if keys != []: print keys
  return keys

class WidgetController():
  def __init__(self):
    pass
  def input(self, keys):
    return keys
  def __call__(self):
    events = pygame.event.get()
    for event in events:
      if event.type == QUIT: 
        pygame.quit(); sys.exit()
      if event.type == pygame.KEYDOWN:
        if event.key == K_ESCAPE:
          pygame.quit(); sys.exit()
    return events




