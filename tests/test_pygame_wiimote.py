'''Unit tests for wiiuse.pygame_wiimote module'''

from unittest.mock import MagicMock, patch
import pytest
import pygame
import wiiuse
import wiiuse.pygame_wiimote as pygame_wm


def setup_module():
    '''Initialize Pygame for event testing.'''
    pygame.init()


def teardown_module():
    '''Quit Pygame after tests finish.'''
    pygame.quit()


def test_event_constants():
    '''Verify event constant values are derived from pygame.USEREVENT.'''
    base = pygame.USEREVENT
    assert pygame_wm.WIIMOTE_BUTTON_PRESS == base + 1
    assert pygame_wm.WIIMOTE_BUTTON_RELEASE == base + 2
    assert pygame_wm.WIIMOTE_ACCEL == base + 3
    assert pygame_wm.WIIMOTE_IR == base + 4
    assert pygame_wm.NUNCHUK_BUTTON_PRESS == base + 5
    assert pygame_wm.NUNCHUK_BUTTON_RELEASE == base + 6
    assert pygame_wm.NUNCHUK_ACCEL == base + 7
    assert pygame_wm.NUNCHUK_JOY == base + 8
    assert pygame_wm.WIIMOTE_STATUS == base + 9
    assert pygame_wm.WIIMOTE_DISCONNECT == base + 10


def test_event_cb_wiimote_buttons():
    '''Test event_cb posts WIIMOTE_BUTTON_PRESS and RELEASE events.'''
    wt = object.__new__(pygame_wm.wiimote_thread)

    wm = MagicMock()
    wm.unid = 1
    wm.btns = wiiuse.button['A']
    wm.btns_held = 0
    wm.btns_released = wiiuse.button['B']
    wm.state = 0  # not using acc, ir, etc.
    wm.exp.type = wiiuse.EXP_NONE

    posted_events = []

    def mock_post(evt):
        posted_events.append(evt)

    with patch('pygame.event.post', side_effect=mock_post):
        wt.event_cb(wm)

    press_events = [e for e in posted_events if e.type == pygame_wm.WIIMOTE_BUTTON_PRESS]
    release_events = [e for e in posted_events if e.type == pygame_wm.WIIMOTE_BUTTON_RELEASE]

    assert len(press_events) == 1
    assert press_events[0].button == 'A'
    assert press_events[0].id == 1

    assert len(release_events) == 1
    assert release_events[0].button == 'B'
    assert release_events[0].id == 1


def test_event_cb_accel_and_ir():
    '''Test event_cb posts WIIMOTE_ACCEL and WIIMOTE_IR events when active.'''
    wt = object.__new__(pygame_wm.wiimote_thread)

    wm = MagicMock()
    wm.unid = 2
    wm.btns = 0
    wm.btns_released = 0
    wm.state = 0x020 | 0x080  # using_acc and using_ir

    wm.orient.roll = 10.0
    wm.orient.pitch = 20.0
    wm.orient.yaw = 30.0
    wm.gforce.x = 0.1
    wm.gforce.y = 0.2
    wm.gforce.z = 0.9

    dot_mocks = []
    for idx in range(4):
        d = MagicMock()
        d.visible = 1 if idx == 0 else 0
        d.x = 100 * idx
        d.y = 200 * idx
        dot_mocks.append(d)

    wm.ir.dot = dot_mocks
    wm.ir.x = 150
    wm.ir.y = 250
    wm.ir.z = 5.0
    wm.exp.type = wiiuse.EXP_NONE

    posted_events = []

    with patch('pygame.event.post', side_effect=posted_events.append):
        wt.event_cb(wm)

    accel_events = [e for e in posted_events if e.type == pygame_wm.WIIMOTE_ACCEL]
    ir_events = [e for e in posted_events if e.type == pygame_wm.WIIMOTE_IR]

    assert len(accel_events) == 1
    assert accel_events[0].orient == (10.0, 20.0, 30.0)
    assert accel_events[0].accel == (0.1, 0.2, 0.9)
    assert accel_events[0].id == 2

    assert len(ir_events) == 1
    assert ir_events[0].dots == [(1, 0, 0), (0, 100, 200), (0, 200, 400), (0, 300, 600)]
    assert ir_events[0].cursor == (150, 250, 5.0)
    assert ir_events[0].id == 2


def test_wiimote_wrapper_methods():
    '''Test Wiimote wrapper class delegate methods to thread execution queue.'''
    mock_wt = MagicMock()
    mock_wm_ptr = MagicMock()
    mock_wt.wiimotes = [mock_wm_ptr]

    with patch.object(pygame_wm, 'WT', mock_wt):
        wm_obj = pygame_wm.Wiimote(0)

        wm_obj.enable_leds(0b0101)  # LEDs 1 and 3 -> LED_1 (0x10) + LED_3 (0x40) = 0x50
        mock_wt.do.assert_called_with(pygame_wm.wiiuse.set_leds, mock_wm_ptr, 0x50)

        wm_obj.enable_rumble(1)
        mock_wt.do.assert_called_with(pygame_wm.wiiuse.rumble, mock_wm_ptr, 1)

        wm_obj.enable_accels(1)
        mock_wt.do.assert_called_with(pygame_wm.wiiuse.motion_sensing, mock_wm_ptr, 1)

        wm_obj.set_orient_thresh(15.0)
        mock_wt.do.assert_called_with(pygame_wm.wiiuse.set_orient_threshold, mock_wm_ptr, 15.0)

        wm_obj.status()
        mock_wt.do.assert_called_with(pygame_wm.wiiuse.status, mock_wm_ptr)


def test_wiimote_wrapper_enable_ir_and_flags():
    '''Test enable_ir and set_flags methods of Wiimote wrapper.'''
    mock_wt = MagicMock()
    mock_wm_ptr = MagicMock()
    mock_wt.wiimotes = [mock_wm_ptr]

    with patch.object(pygame_wm, 'WT', mock_wt):
        wm_obj = pygame_wm.Wiimote(0)

        wm_obj.enable_ir(1, vres=(1024, 768), position=0, aspect=1)
        mock_wt.do.assert_any_call(pygame_wm.wiiuse.set_ir, mock_wm_ptr, 1)
        mock_wt.do.assert_any_call(pygame_wm.wiiuse.set_ir_vres, mock_wm_ptr, 1024, 768)
        mock_wt.do.assert_any_call(pygame_wm.wiiuse.set_ir_position, mock_wm_ptr, 0)
        mock_wt.do.assert_any_call(pygame_wm.wiiuse.set_aspect_ratio, mock_wm_ptr, 1)

        mock_wt.reset_mock()

        # set_flags(smoothing=True, continuous=False, threshold=True)
        # enable = SMOOTHING (0x01) | ORIENT_THRESH (0x04) = 0x05
        # disable = CONTINUOUS (0x02)
        wm_obj.set_flags(smoothing=True, continuous=False, threshold=True)
        mock_wt.do.assert_called_with(pygame_wm.wiiuse.set_flags, mock_wm_ptr, 0x05, 0x02)
