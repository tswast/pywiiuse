'''Access to the Wiimote in pygame

I tried to mimic the Joystick interface already in pygame.

The usuage pattern is 

init the module telling it the maximum number of wiimotes and the timeout
get_count to determine how many you got
Wiimote(n) to get an object referencing the nth wiimote

Free for any use. If you or your lawyer are stupid enough to believe I have any liability for
this, then don't use it; otherwise be my guest.

Gary Bishop January 2008

'''

import pygame
from threading import Thread
from Queue import Queue, Empty
import time

# events to use. Is there a way to get ones known to be unused?
base = pygame.USEREVENT
WIIMOTE_BUTTON_PRESS = base + 1
WIIMOTE_BUTTON_RELEASE = base + 2
WIIMOTE_ACCEL = base + 3
WIIMOTE_IR = base + 4
NUNCHUK_BUTTON_PRESS = base + 5
NUNCHUK_BUTTON_RELEASE = base + 6
NUNCHUK_ACCEL = base + 7
NUNCHUK_JOY = base + 8
WIIMOTE_STATUS = base + 9
WIIMOTE_DISCONNECT = base + 10

wiiuse = None # import within the thread, why do I have to do this?

class wiimote_thread(Thread):
    '''Manage the wiiuse interface'''
    def __init__(self, nmotes=1, timeout=5):
        Thread.__init__(self, name='wiimote')
        self.queue = Queue()
        self.startup = Queue()
        self.nmotes = nmotes
        self.timeout = timeout
        self.setDaemon(1)
        self.start()
        self.startup.get(True) # wait for the thread to get started and acquire the motes

    def run(self):
        '''This runs in a separate thread'''
        # import here to avoid thread problems on windows
        global wiiuse
        import wiiuse
        
        self.wiimotes = wiiuse.init(self.nmotes)
        found = wiiuse.find(self.wiimotes, self.nmotes, self.timeout)
        self.actual_nmotes = wiiuse.connect(self.wiimotes, self.nmotes)

        for i in range(self.nmotes):
            wiiuse.set_leds(self.wiimotes[i], wiiuse.LED[i])

        self.go = self.actual_nmotes != 0

        self.startup.put(self.go)

        while self.go:
            try:
                if wiiuse.poll(self.wiimotes, self.nmotes):
                    for i in range(self.nmotes):
                        wm = self.wiimotes[i][0]
                        if wm.event:
                            self.event_cb(wm)

            except:
                pass

            # allow executing functions in this thread
            while True:
                try:
                    func, args = self.queue.get_nowait()
                except Empty:
                    break
                func(*args)

    def do(self, func, *args):
        '''Run the function in the thread handling the wiimote'''
        self.queue.put((func, args))

    def event_cb(self, wm):
        '''Called when the library has some data for the user.'''
        
        if wm.btns:
            for name,b in wiiuse.button.items():
                if wiiuse.is_just_pressed(wm, b):
                    pygame.event.post(pygame.event.Event(WIIMOTE_BUTTON_PRESS, button=name,
                                                         time=time.time(),
                                                         id=wm.unid))

        if wm.btns_released:
            for name,b in wiiuse.button.items():
                if wiiuse.is_released(wm, b):
                    pygame.event.post(pygame.event.Event(WIIMOTE_BUTTON_RELEASE, button=name,
                                                         time=time.time(),
                                                         id=wm.unid))

        if wiiuse.using_acc(wm):
            pygame.event.post(pygame.event.Event(WIIMOTE_ACCEL, 
                                                 orient=(wm.orient.roll, wm.orient.pitch,
                                                         wm.orient.yaw),
                                                 accel=(wm.gforce.x, wm.gforce.y, wm.gforce.z),
                                                 time=time.time(),
                                                 id=wm.unid))
        if wiiuse.using_ir(wm):
            dots = [ (wm.ir.dot[i].visible, wm.ir.dot[i].x, wm.ir.dot[i].y) for i in range(4) ]
            pygame.event.post(pygame.event.Event(WIIMOTE_IR,
                                                 dots=dots,
                                                 cursor=(wm.ir.x, wm.ir.y, wm.ir.z),
                                                 time=time.time(),
                                                 id=wm.unid))

        if wm.exp.type == wiiuse.EXP_NUNCHUK:
            nc = wm.exp.u.nunchuk
            
            for name,b in wiiuse.nunchuk_button.items():
                if wiiuse.is_just_pressed(nc, b):
                    pygame.event.post(pygame.event.Event(NUNCHUK_BUTTON_PRESS, button=name,
                                                         time=time.time(),
                                                         id=wm.unid))
                elif wiiuse.is_released(nc, b):
                    pygame.event.post(pygame.event.Event(NUNCHUK_BUTTON_RELEASE, button=name,
                                                         time=time.time(),
                                                         id=wm.unid))

            pygame.event.post(pygame.event.Event(NUNCHUK_ACCEL,
                                                 orient=(nc.orient.roll, nc.orient.pitch,
                                                         nc.orient.yaw),
                                                 accel=(nc.gforce.x, nc.gforce.y, nc.gforce.z),
                                                 time=time.time(),
                                                 id=wm.unid))
            pygame.event.post(pygame.event.Event(NUNCHUK_JOY,
                                                 angle=nc.js.ang,
                                                 mag=nc.js.mag,
                                                 time=time.time(),
                                                 id=wm.unid))

    def quit(self):
        '''Go away.'''
        for i in range(self.nmotes):
            wiiuse.set_leds(self.wiimotes[i], 0)
            wiiuse.disconnect(self.wiimotes[i])
        self.go = False

WT = None

def init(nmotes, timeout):
    '''Initialize the module.'''
    global WT
    if WT:
        return
    WT = wiimote_thread(nmotes, timeout)

def get_count():
    '''How many Wiimotes were found?'''
    return WT.actual_nmotes

def quit():
    '''Gracefully shutdown the connection and turn off the wiimote leds'''
    WT.quit()
    WT.join()

class wiimote(object):
    '''Object representing a Wiimote'''
    def __init__(self, n):
        self.wm = WT.wiimotes[n]

    def enable_leds(self, m):
        '''Control leds. The lower 4 bits map to the 4 leds'''
        WT.do(wiiuse.set_leds, self.wm, sum([wiiuse.LED[i] for i in range(4) if m & (1<<i)]))

    def enable_rumble(self, on):
        '''Control rumble'''
        WT.do(wiiuse.rumble, self.wm, on)

    def enable_accels(self, on):
        '''Control reporting of accelerometer data.'''
        WT.do(wiiuse.motion_sensing, self.wm, on)

    def enable_ir(self, on, vres=None, position=None, aspect=None):
        '''Control reporting IR data.'''
        WT.do(wiiuse.set_ir, self.wm, on)
        if vres is not None:
            WT.do(wiiuse.set_ir_vres, self.wm, vres[0], vres[1])
        if position is not None:
            WT.do(wiiuse.set_ir_position, self.wm, position)
        if aspect is not None:
            WT.do(wiiuse.set_aspect_ratio, self.wm, aspect)

    def set_flags(self, smoothing=None, continuous=None, threshold=None):
        '''Set flags SMOOTHING, CONTINUOUS, ORIENT_THRESH'''
        enable = disable = 0
        if smoothing is not None:
            if smoothing:
                enable |= wiiuse.SMOOTHING
            else:
                disable |= wiiuse.SMOOTHING
        if continuous is not None:
            if continuous:
                enable |= wiiuse.CONTINUOUS
            else:
                disable |= wiiuse.CONTINUOUS
        if threshold is not None:
            if threshold:
                enable |= wiiuse.ORIENT_THRESH
            else:
                disable |= wiiuse.ORIENT_THRESH
        print enable, disable
        WT.do(wiiuse.set_flags, self.wm, enable, disable)

    def set_orient_thresh(self, thresh):
        '''Set orientation threshold'''
        WT.do(wiiuse.set_orient_threshold, self.wm, thresh)

    def status(self):
        '''Trigger a status callback.'''
        WT.do(wiiuse.status, self.wm)

    def disconnect(self):
        '''Disconnect this Wiimote'''
        WT.do(wiiuse.disconnect(self.wm))

def Wiimote(n):
    '''Get the object for the nth Wiimote'''
    return wiimote(n)

