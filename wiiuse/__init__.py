'''Python interface to the wiiuse library for the wii remote

Just a simple wrapper, no attempt to make the api pythonic. I tried to hide ctypes where
necessary.

This software is free for any use. If you or your lawyer are stupid enough to believe I have any
liability for it, then don't use it; otherwise, be my guest.

Gary Bishop, January 2008
'''

import os
import sys
import ctypes
from ctypes import (c_char_p, c_int, c_int16, c_uint16, c_byte, c_uint, c_uint8, c_float,
    c_void_p, c_char, c_short, c_ushort)
from ctypes import CFUNCTYPE, Structure, POINTER, Union, byref

# duplicate the wiiuse data structures

class ang3s(Structure):
    _fields_ = [('roll', c_int16),
                ('pitch', c_int16),
                ('yaw', c_int16)
                ]

class ang3f(Structure):
    _fields_ = [('roll', c_float),
                ('pitch', c_float),
                ('yaw', c_float)
                ]

class vec2b(Structure):
    _fields_ = [('x', c_byte),
                ('y', c_byte),
                ]

class vec3b(Structure):
    _fields_ = [('x', c_byte),
                ('y', c_byte),
                ('z', c_byte),
                ]

class vec3f(Structure):
    _fields_ = [('x', c_float),
                ('y', c_float),
                ('z', c_float),
                ]

class orient(Structure):
    _fields_ = [('roll', c_float),
                ('pitch', c_float),
                ('yaw', c_float),
                ('a_roll', c_float),
                ('a_pitch', c_float),
                ]

class accel(Structure):
    _fields_ = [('cal_zero', vec3b),
                ('cal_g', vec3b),
                ('st_roll', c_float),
                ('st_pitch', c_float),
                ('st_alpha', c_float),
                ]

class ir_dot(Structure):
    _fields_ = [('visible', c_byte),
                ('x', c_uint),
                ('y', c_uint),
                ('rx', c_int16),
                ('ry', c_int16),
                ('order', c_byte),
                ('size', c_byte),
                ]

class ir(Structure):
    _fields_ = [('dot', ir_dot*4),
                ('num_dots', c_byte),
                ('aspect', c_int),
                ('pos', c_int),
                ('vres', c_uint*2),
                ('offset', c_int*2),
                ('state', c_int),
                ('ax', c_int),
                ('ay', c_int),
                ('x', c_int),
                ('y', c_int),
                ('distance', c_float),
                ('z', c_float),
                ]

class joystick(Structure):
    _fields_ = [('max', vec2b),
                ('min', vec2b),
                ('center', vec2b),
                ('ang', c_float),
                ('mag', c_float),
                ]

class nunchuk(Structure):
    _fields_ = [('accel_calib', accel),
                ('js', joystick),
                ('flags', POINTER(c_int)),
                ('btns', c_byte),
                ('btns_held', c_byte),
                ('btns_released', c_byte),
                ('orient_threshold', c_float),
                ('accel_threshold', c_int),
                ('accel', vec3b),
                ('orient', orient),
                ('gforce', vec3f),
                ]

class classic_ctrl(Structure):
    _fields_ = [('btns', c_int16),
                ('btns_held', c_int16),
                ('btns_released', c_int16),
                ('r_shoulder', c_float),
                ('l_shoulder', c_float),
                ('ljs', joystick),
                ('rjs', joystick),
                ]

class guitar_hero_3(Structure):
    _fields_ = [('btns', c_int16),
                ('btns_held', c_int16),
                ('btns_released', c_int16),
                ('whammy_bar', c_float),
                ('js', joystick),
                ]
class motion_plus(Structure):
    _fields_ = [('ext', c_byte),
                ('raw_gyro', ang3s),
                ('cal_gyro', ang3s),
                ('angle_rate_gyro', ang3f),
                ('orient', orient),
                ('acc_mode', c_byte),
                ('raw_gyro_threshold', c_int),
                ('nunchuk', POINTER(nunchuk)),
                ('classic_ctrl', POINTER(classic_ctrl)),
                ]
class wii_board(Structure):
    _fields_ = [('tl', c_float),
                ('tr', c_float),
                ('bl', c_float),
                ('br', c_float),
                ('rtl', c_ushort),
                ('rtr', c_ushort),
                ('rbl', c_ushort),
                ('rbr', c_ushort),
                ('ctl', c_ushort*3),
                ('ctr', c_ushort*3),
                ('cbl', c_ushort*3),
                ('cbr', c_ushort*3),
                ('update_calib', c_uint8),
                ('use_alternate_report', c_uint8),
                ]
class expansion_union(Union):
    _fields_ = [('nunchuk', nunchuk),
                ('classic', classic_ctrl),
                ('gh3', guitar_hero_3),
                ('wb', wii_board),
                ]

class expansion(Structure):
    _fields_ = [('type', c_int),
                ('motion_plus', motion_plus),
                ('u', expansion_union),
                ]

class wiimote_state(Structure):
    _fields_ = [('exp_ljs_ang', c_float),
                ('exp_rjs_ang', c_float),
                ('exp_ljs_mag', c_float),
                ('exp_rjs_mag', c_float),
                ('exp_btns', c_uint16),
                ('exp_orient', orient),
                ('exp_accel', vec3b),
                ('exp_r_shoulder', c_float),
                ('exp_l_shoulder', c_float),
				('drx', c_short),
				('dry', c_short),
				('drz', c_short),
				('exp_wb_rtr', c_uint16),
				('exp_wb_rtl', c_uint16),
				('exp_wb_rbr', c_uint16),
				('exp_wb_rbl', c_uint16),
                ('ir_ax', c_int),
                ('ir_ay', c_int),
                ('ir_distance', c_float),
                ('orient', orient),
                ('btns', c_uint16),
                ('accel', vec3b),
                ]

if os.name == 'nt':
    JunkSkip = [('dev_handle', c_void_p),
                ('hid_overlap', c_void_p*5), # skipping over this data structure
                ('stack', c_int),
                ('timeout',c_int),#added
				('normal_timeout',c_byte),#added
				('exp_timeout',c_byte)#added
                ]
elif sys.platform == 'darwin':
    JunkSkip = [('objc_wm', c_void_p)]
else:
    JunkSkip = [('bdaddr', c_void_p),
                ('bdaddr_str', c_char*18),
                ('out_sock', c_int),
                ('in_sock', c_int),
                ]

class wiimote(Structure):
    _fields_ = [('unid', c_int),
                ] + JunkSkip + [
                ('state', c_int),
                ('leds', c_byte),
                ('battery_level', c_float),
                ('flags', c_int),
                ('handshake_state', c_byte),
                ('expansion_state', c_byte),
                ('data_req', c_void_p),
                ('read_req', c_void_p),
                ('accel_calib', accel),
                ('exp', expansion),
                ('accel', vec3b),
                ('orient', orient),
                ('gforce', vec3f),
                ('ir', ir),
                ('btns', c_ushort),
                ('btns_held', c_ushort),
                ('btns_released', c_ushort),
                ('orient_threshold', c_float),
                ('accel_threshold', c_int),
                ('lstate', wiimote_state),
                ('event', c_int),
                ('motion_plus_id', c_byte*6)
                ]

wiimote_p = POINTER(wiimote)
wiimote_pp = POINTER(wiimote_p)

event_cb_t = CFUNCTYPE(None, wiimote_p)
read_cb_t = CFUNCTYPE(None, wiimote_p, POINTER(c_byte), c_ushort)
ctrl_status_cb_t = CFUNCTYPE(None, wiimote_p, c_int, c_int, c_int, POINTER(c_int), c_float)
dis_cb_t = CFUNCTYPE(None, wiimote_p)

# clearly a few more to do but I haven't needed them yet
class api(Structure):
    _fields_ = [('version', c_char_p),
                ('api_version', c_int),
                ('init', CFUNCTYPE(wiimote_pp, c_int, POINTER(c_int), event_cb_t, 
                                   ctrl_status_cb_t, dis_cb_t)),
                ('disconnected', c_void_p),
                ('rumble', CFUNCTYPE(None, wiimote_p, c_int)),
                ('toggle_rumble', CFUNCTYPE(None, wiimote_p)),
                ('set_leds', CFUNCTYPE(None, wiimote_p, c_int)),
                ('motion_sensing', CFUNCTYPE(None, wiimote_p, c_int)),
                ('read_data', c_void_p),
                ('write_data', c_void_p),
                ('status', CFUNCTYPE(None, wiimote_p)),
                ('get_by_id', CFUNCTYPE(wiimote_p, wiimote_pp, c_int, c_int)),
                ('set_flags', CFUNCTYPE(c_int, wiimote_p, c_int, c_int)),
                ('set_smooth_alpha', CFUNCTYPE(c_float, wiimote_p, c_float)),
                ('set_ir', CFUNCTYPE(None, wiimote_p, c_int)),
                ('set_ir_vres', CFUNCTYPE(None, wiimote_p, c_uint, c_uint)),
                ('set_ir_position', CFUNCTYPE(None, wiimote_p, c_int)),
                ('set_aspect_ratio', CFUNCTYPE(None, wiimote_p, c_int)),
                ('set_bluetooth_stack', c_void_p),
                ('set_orient_threshold', CFUNCTYPE(None, wiimote_p, c_float)),
                ('find', CFUNCTYPE(c_int, wiimote_pp, c_int, c_int)),
                ('connect', CFUNCTYPE(c_int, wiimote_pp, c_int)),
                ('disconnect', CFUNCTYPE(None, wiimote_p)),
                ('poll', CFUNCTYPE(None, wiimote_pp, c_int)),
                ('set_timeout', CFUNCTYPE(None, wiimote_pp, c_int, c_char, c_char)),
                ]

def is_pressed(dev, button):
    return dev.btns & button

def is_held(dev, button):
    return dev.btns_held & button

def is_released(dev, button):
    return dev.btns_released & button

def is_just_pressed(dev, button):
    return is_pressed(dev, button) and not is_held(dev, button)

def using_acc(wm):
    return wm.state & 0x020

def using_exp(wm):
    return wm.state & 0x040

def using_ir(wm):
    return wm.state & 0x080

def using_speaker(wm):
    return wm.state & 0x100

LED_NONE = 0
LED_1 = 0x10
LED_2 = 0x20
LED_3 = 0x40
LED_4 = 0x80

LED = [LED_1, LED_2, LED_3, LED_4]

EXP_NONE = 0
EXP_NUNCHUK = 1
EXP_CLASSIC = 2

SMOOTHING = 0x01
CONTINUOUS = 0x02
ORIENT_THRESH = 0x04
INIT_FLAGS = SMOOTHING | ORIENT_THRESH

IR_ABOVE = 0
IR_BELOW = 1

ASPECT_4_3 = 0
ASPECT_16_9 = 1

button = { '2':0x0001,
           '1':0x0002,
           'B':0x0004,
           'A':0x0008,
           '-':0x0010,
           'Home':0x0080,
           'Left':0x0100,
           'Right':0x0200,
           'Down':0x0400,
           'Up':0x0800,
           '+':0x1000,
           }

nunchuk_button = { 'Z':0x01,
                   'C':0x02,
                   }

# functions from the wiiuse api
find = None
connect = None
set_leds = None
rumble = None
status = None
poll = None
disconnect = None
motion_sensing = None
set_ir = None
toggle_rumble = None
set_ir_vres = None
set_ir_position = None
set_aspect_ratio = None
set_orient_threshold = None
set_flags = None
get_by_id = None
set_timeout = None

NONE = 0
EVENT = 1
STATUS = 2
CONNECT = 3
DISCONNECT = 4
UNEXPECTED_DISCONNECT = 5
READ_DATA = 6
WRITE_DATA = 7
NUNCHUK_INSERTED = 8
NUNCHUK_REMOVED = 9
CLASSIC_CTRL_INSERTED = 10
CLASSIC_CTRL_REMOVED = 11
GUITAR_HERO_3_CTRL_INSERTED = 12
GUITAR_HERO_3_CTRL_REMOVED = 13
WII_BOARD_CTRL_INSERTED = 14
WII_BOARD_CTRL_REMOVED = 15
MOTION_PLUS_ACTIVATED = 16
MOTION_PLUS_REMOVED = 17

# wrap the init function so the user doesn't have to fool with ctypes for the callbacks
def init(nwiimotes):
    '''Initialize the module'''
    # find the dll
    if os.name == 'nt':
        dll = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libwiiuse.dll"))
    elif sys.platform == 'darwin':
        dll = ctypes.cdll.LoadLibrary('libwiiuse.dylib')
    else:
        dll = ctypes.cdll.LoadLibrary('libwiiuse.so')

    # pointer to the api object he will return
    # wiiuse_api = POINTER(api)()
    # fill in the pointer
    # dll.wiiuse_main(byref(wiiuse_api))
    # get the object so we don't have to fool with the pointer
    # wapi = wiiuse_api[0]

    # initialize our other function pointers
    global find, connect, set_leds, rumble, status, poll, disconnect, motion_sensing
    global set_ir, toggle_rumble, set_ir_vres, set_ir_position, set_aspect_ratio
    global set_orient_threshold, set_flags, get_by_id, set_timeout
    find = dll.wiiuse_find
    connect = dll.wiiuse_connect
    set_leds = dll.wiiuse_set_leds
    rumble = dll.wiiuse_rumble
    status = dll.wiiuse_status
    poll = dll.wiiuse_poll
    disconnect = dll.wiiuse_disconnect
    motion_sensing = dll.wiiuse_motion_sensing
    set_ir = dll.wiiuse_set_ir
    toggle_rumble = dll.wiiuse_toggle_rumble
    set_ir_vres = dll.wiiuse_set_ir_vres
    set_ir_position = dll.wiiuse_set_ir_position
    set_aspect_ratio = dll.wiiuse_set_aspect_ratio
    set_orient_threshold = dll.wiiuse_set_orient_threshold
    set_flags = dll.wiiuse_set_flags
    get_by_id = dll.wiiuse_get_by_id
    set_timeout = dll.wiiuse_set_timeout
    
    # finally initialize wiiuse
    dll.wiiuse_init.restype = wiimote_pp
    wiimotes = dll.wiiuse_init(nwiimotes)

    return wiimotes

