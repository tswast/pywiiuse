#! /usr/bin/python

'''Try to implement the example in python'''

import wiiuse

import sys
import time
import os

nmotes = 2

def handle_event(wmp):
    wm = wmp[0]
    print '--- EVENT [wiimote id %i] ---' % wm.unid
    
    if wm.btns:
        for name, b in wiiuse.button.items():
            if wiiuse.is_pressed(wm, b):
                print name,'pressed'

        if wiiuse.is_just_pressed(wm, wiiuse.button['-']):
            wiiuse.motion_sensing(wmp, 0)
        if wiiuse.is_just_pressed(wm, wiiuse.button['+']):
            wiiuse.motion_sensing(wmp, 1)
        if wiiuse.is_just_pressed(wm, wiiuse.button['B']):
            wiiuse.toggle_rumble(wmp)
        if wiiuse.is_just_pressed(wm, wiiuse.button['Up']):
            wiiuse.set_ir(wmp, 1)
        if wiiuse.is_just_pressed(wm, wiiuse.button['Down']):
            wiiuse.set_ir(wmp, 0)
    
    if wiiuse.using_acc(wm):
        print 'roll  = %f' % wm.orient.roll
        print 'pitch = %f' % wm.orient.pitch
        print 'yaw   = %f' % wm.orient.yaw
    
    if wiiuse.using_ir(wm):
        for i in range(4):
            if wm.ir.dot[i].visible:
                print 'IR source %i: (%u, %u)' % (i, wm.ir.dot[i].x, wm.ir.dot[i].y)
        print 'IR cursor: (%u, %u)' % (wm.ir.x, wm.ir.y)
        print 'IR z distance: %f' % wm.ir.z

    if wm.exp.type == wiiuse.EXP_NUNCHUK:
        nc = wm.exp.u.nunchuk
        
        for name,b in wiiuse.nunchuk_button.items():
            if wiiuse.is_pressed(nc, b):
                print 'Nunchuk: %s is pressed' % name

        print 'nunchuk roll  = %f' % nc.orient.roll
        print 'nunchuk pitch = %f' % nc.orient.pitch
        print 'nunchuk yaw   = %f' % nc.orient.yaw
        print 'nunchuk joystick angle:     %f' % nc.js.ang
        print 'nunchuk joystick magnitude: %f' % nc.js.mag


def handle_ctrl_status(wmp, attachment, speaker, ir, led, battery_level):
    wm = wmp[0]
    print '--- Controller Status [wiimote id %i] ---' % wm.unid
    print 'attachment', attachment
    print 'speaker', speaker
    print 'ir', ir
    print 'leds', led[0], led[1], led[2], led[3]
    print 'battery', battery_level

def handle_disconnect(wmp):
    print 'disconnect'

if os.name != 'nt': print 'Press 1&2'

wiimotes = wiiuse.init(nmotes)

found = wiiuse.find(wiimotes, nmotes, 5)
if not found:
    print 'not found'
    sys.exit(1)

connected = wiiuse.connect(wiimotes, nmotes)
if connected:
    print 'Connected to %i wiimotes (of %i found).' % (connected, found)
else:
    print 'failed to connect to any wiimote.'
    sys.exit(1)

for i in range(nmotes):
    wiiuse.set_leds(wiimotes[i], wiiuse.LED[i])
    wiiuse.status(wiimotes[0])
    wiiuse.set_ir(wiimotes[0], 1)
    wiiuse.set_ir_vres(wiimotes[i], 1000, 1000)

try:
    rum = 1
    while True:
        r = wiiuse.poll(wiimotes, nmotes)
        if r != 0:
            handle_event(wiimotes[0])
except KeyboardInterrupt:
    for i in range(nmotes):
        wiiuse.set_leds(wiimotes[i], 0)
        wiiuse.rumble(wiimotes[i], 0)
        wiiuse.disconnect(wiimotes[i])

print 'done'

