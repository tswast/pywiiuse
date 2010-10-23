'''Test thw wiimote extension for pygame

I stole the graphing from wiiewer and then hacked it to work without Numeric

'''

import pygame
import wiiuse.pygame_wiimote as pygame_wiimote
import sys
import time
import os

pygame.init()

# initialze the wiimotes
if os.name != 'nt': print 'press 1&2'
pygame_wiimote.init(1, 5) # look for 1, wait 5 seconds
n = pygame_wiimote.get_count() # how many did we get?

if n == 0:
    print 'no wiimotes found'
    sys.exit(1)

w,h = size = (512,512)

wm = pygame_wiimote.Wiimote(0) # access the wiimote object
wm.enable_accels(1) # turn on acceleration reporting
wm.enable_ir(1, vres=size) # turn on ir reporting

screen = pygame.display.set_mode(size)

run = True

old = [h/2] * 6
maxA = 2.0

colors = [ (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255, 0, 255), (0,255,255) ]

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print 'quiting'
            run = False
            break
        elif event.type in [ pygame_wiimote.WIIMOTE_BUTTON_PRESS,
                             pygame_wiimote.NUNCHUK_BUTTON_PRESS ]:
            print event.button, 'pressed on', event.id
        elif event.type in [ pygame_wiimote.WIIMOTE_BUTTON_RELEASE,
                             pygame_wiimote.NUNCHUK_BUTTON_RELEASE ]:
            print event.button, 'released on', event.id
        elif event.type in [ pygame_wiimote.WIIMOTE_ACCEL, pygame_wiimote.NUNCHUK_ACCEL ]:
            if event.type == pygame_wiimote.WIIMOTE_ACCEL:
                b = 0
            else:
                b = 3
            for c in range(3):
                s = int((event.accel[c] * h / maxA + h)/2)
                s = max(0, min(h-1, s))
                pygame.draw.line(screen, colors[b+c], (w-3, old[b+c]), (w-2, s))
                old[b+c] = s
            screen.blit(screen, (-1, 0))
        elif event.type == pygame_wiimote.WIIMOTE_STATUS:
            print 'status', event.dict
        elif event.type == pygame_wiimote.WIIMOTE_DISCONNECT:
            print 'disconnected'
            run = False
            break
        elif event.type == pygame_wiimote.WIIMOTE_IR:
            pygame.draw.circle(screen, colors[5], event.cursor[:2], 10)

    pygame.display.flip()
    pygame.time.wait(10)
pygame_wiimote.quit()


