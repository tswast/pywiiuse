'''Unit tests for wiiuse core module'''

import ctypes
from unittest.mock import MagicMock, patch
import pytest
import wiiuse


class DummyDev:
    def __init__(self, btns=0, btns_held=0, btns_released=0):
        self.btns = btns
        self.btns_held = btns_held
        self.btns_released = btns_released


class DummyWiimote:
    def __init__(self, state=0):
        self.state = state


def test_structures_instantiation():
    '''Verify ctypes structures can be instantiated and fields exist.'''
    a3s = wiiuse.ang3s(roll=10, pitch=20, yaw=30)
    assert a3s.roll == 10
    assert a3s.pitch == 20
    assert a3s.yaw == 30

    a3f = wiiuse.ang3f(roll=1.5, pitch=2.5, yaw=3.5)
    assert pytest.approx(a3f.roll) == 1.5
    assert pytest.approx(a3f.pitch) == 2.5
    assert pytest.approx(a3f.yaw) == 3.5

    v2b = wiiuse.vec2b(x=1, y=2)
    assert v2b.x == 1
    assert v2b.y == 2

    v3b = wiiuse.vec3b(x=1, y=2, z=3)
    assert v3b.x == 1
    assert v3b.y == 2
    assert v3b.z == 3

    v3f = wiiuse.vec3f(x=1.0, y=2.0, z=3.0)
    assert pytest.approx(v3f.x) == 1.0
    assert pytest.approx(v3f.y) == 2.0
    assert pytest.approx(v3f.z) == 3.0

    o = wiiuse.orient(roll=1.0, pitch=2.0, yaw=3.0, a_roll=4.0, a_pitch=5.0)
    assert pytest.approx(o.roll) == 1.0
    assert pytest.approx(o.a_pitch) == 5.0

    acc = wiiuse.accel(st_roll=1.0, st_pitch=2.0, st_alpha=3.0)
    assert pytest.approx(acc.st_roll) == 1.0

    dot = wiiuse.ir_dot(visible=1, x=100, y=200, rx=10, ry=20, order=1, size=5)
    assert dot.visible == 1
    assert dot.x == 100
    assert dot.y == 200

    ir_obj = wiiuse.ir(num_dots=2, aspect=0, pos=1, distance=10.5, z=5.0)
    assert ir_obj.num_dots == 2
    assert pytest.approx(ir_obj.distance) == 10.5

    js = wiiuse.joystick(ang=45.0, mag=0.8, x=0.5, y=0.5)
    assert pytest.approx(js.ang) == 45.0
    assert pytest.approx(js.mag) == 0.8

    nc = wiiuse.nunchuk(btns=1, btns_held=0, btns_released=0)
    assert nc.btns == 1

    classic = wiiuse.classic_ctrl(btns=4, r_shoulder=0.5, l_shoulder=0.8)
    assert classic.btns == 4

    gh3 = wiiuse.guitar_hero_3(btns=2, whammy_bar=0.1)
    assert gh3.btns == 2

    wb = wiiuse.wii_board(tl=1.1, tr=2.2, bl=3.3, br=4.4)
    assert pytest.approx(wb.tl) == 1.1

    wm = wiiuse.wiimote(unid=1, leds=0x10, battery_level=0.75, btns=8)
    assert wm.unid == 1
    assert wm.leds == 0x10
    assert pytest.approx(wm.battery_level) == 0.75
    assert wm.btns == 8


def test_button_helpers():
    '''Test helper functions for button pressed, held, released, and just pressed.'''
    dev = DummyDev(btns=wiiuse.button['A'] | wiiuse.button['B'],
                   btns_held=wiiuse.button['A'],
                   btns_released=wiiuse.button['Up'])

    assert wiiuse.is_pressed(dev, wiiuse.button['A'])
    assert wiiuse.is_pressed(dev, wiiuse.button['B'])
    assert not wiiuse.is_pressed(dev, wiiuse.button['Up'])

    assert wiiuse.is_held(dev, wiiuse.button['A'])
    assert not wiiuse.is_held(dev, wiiuse.button['B'])

    assert wiiuse.is_released(dev, wiiuse.button['Up'])
    assert not wiiuse.is_released(dev, wiiuse.button['A'])

    # Button B is pressed, but NOT held -> just pressed
    assert wiiuse.is_just_pressed(dev, wiiuse.button['B'])
    # Button A is pressed AND held -> not just pressed
    assert not wiiuse.is_just_pressed(dev, wiiuse.button['A'])


def test_state_helpers():
    '''Test bitmask checkers for accelerometer, expansion, IR, and speaker.'''
    wm_acc = DummyWiimote(state=0x020)
    wm_exp = DummyWiimote(state=0x040)
    wm_ir = DummyWiimote(state=0x080)
    wm_spk = DummyWiimote(state=0x100)
    wm_all = DummyWiimote(state=0x020 | 0x040 | 0x080 | 0x100)
    wm_none = DummyWiimote(state=0x000)

    assert wiiuse.using_acc(wm_acc)
    assert not wiiuse.using_acc(wm_none)

    assert wiiuse.using_exp(wm_exp)
    assert not wiiuse.using_exp(wm_none)

    assert wiiuse.using_ir(wm_ir)
    assert not wiiuse.using_ir(wm_none)

    assert wiiuse.using_speaker(wm_spk)
    assert not wiiuse.using_speaker(wm_none)

    assert wiiuse.using_acc(wm_all)
    assert wiiuse.using_exp(wm_all)
    assert wiiuse.using_ir(wm_all)
    assert wiiuse.using_speaker(wm_all)


def test_constants():
    '''Test values of exported module constants.'''
    assert wiiuse.LED_NONE == 0
    assert wiiuse.LED_1 == 0x10
    assert wiiuse.LED_2 == 0x20
    assert wiiuse.LED_3 == 0x40
    assert wiiuse.LED_4 == 0x80
    assert wiiuse.LED == [0x10, 0x20, 0x40, 0x80]

    assert wiiuse.EXP_NONE == 0
    assert wiiuse.EXP_NUNCHUK == 1
    assert wiiuse.EXP_CLASSIC == 2

    assert wiiuse.SMOOTHING == 0x01
    assert wiiuse.CONTINUOUS == 0x02
    assert wiiuse.ORIENT_THRESH == 0x04
    assert wiiuse.INIT_FLAGS == (wiiuse.SMOOTHING | wiiuse.ORIENT_THRESH)

    assert wiiuse.IR_ABOVE == 0
    assert wiiuse.IR_BELOW == 1

    assert wiiuse.ASPECT_4_3 == 0
    assert wiiuse.ASPECT_16_9 == 1

    # Check button mappings
    assert wiiuse.button['A'] == 0x0008
    assert wiiuse.button['B'] == 0x0004
    assert wiiuse.button['1'] == 0x0002
    assert wiiuse.button['2'] == 0x0001
    assert wiiuse.button['-'] == 0x0010
    assert wiiuse.button['+'] == 0x1000
    assert wiiuse.button['Home'] == 0x0080
    assert wiiuse.button['Left'] == 0x0100
    assert wiiuse.button['Right'] == 0x0200
    assert wiiuse.button['Down'] == 0x0400
    assert wiiuse.button['Up'] == 0x0800

    # Nunchuk buttons
    assert wiiuse.nunchuk_button['Z'] == 0x01
    assert wiiuse.nunchuk_button['C'] == 0x02

    # Events
    assert wiiuse.NONE == 0
    assert wiiuse.EVENT == 1
    assert wiiuse.STATUS == 2
    assert wiiuse.CONNECT == 3
    assert wiiuse.DISCONNECT == 4
    assert wiiuse.UNEXPECTED_DISCONNECT == 5


@patch('ctypes.cdll.LoadLibrary')
def test_init(mock_load_library):
    '''Test wiiuse.init with mocked C library.'''
    mock_dll = MagicMock()
    mock_load_library.return_value = mock_dll

    fake_wiimotes = MagicMock()
    mock_dll.wiiuse_init.return_value = fake_wiimotes

    result = wiiuse.init(2)

    mock_load_library.assert_called_once()
    mock_dll.wiiuse_init.assert_called_once_with(2)
    assert result == fake_wiimotes
    assert wiiuse.find == mock_dll.wiiuse_find
    assert wiiuse.connect == mock_dll.wiiuse_connect
    assert wiiuse.set_leds == mock_dll.wiiuse_set_leds
    assert wiiuse.rumble == mock_dll.wiiuse_rumble
    assert wiiuse.status == mock_dll.wiiuse_status
    assert wiiuse.poll == mock_dll.wiiuse_poll
    assert wiiuse.disconnect == mock_dll.wiiuse_disconnect
    assert wiiuse.motion_sensing == mock_dll.wiiuse_motion_sensing
