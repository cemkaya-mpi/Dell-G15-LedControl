#!/usr/bin/python3
import sys
import argparse
import random
from elc import *
from elc_constants import *


DURATION_MAX = 0xffff
DURATION_BATTERY_LOW = 0xff
DURATION_MIN = 0x00
TEMPO_MAX = 0xff
TEMPO_MIN = 0x01
ZONES = [0, 1, 2, 3]


def init_device():
    # So that we don't get an USB device busy error
    device = usb.core.find(idVendor=0x187c, idProduct=0x0550)
    ep = device[0].interfaces()[0].endpoints()[0]
    i = device[0].interfaces()[0].bInterfaceNumber
    device.reset()
    if device.is_kernel_driver_active(i):
        device.detach_kernel_driver(i)

    # Create the elc object
    vid = 0x187C
    pid = 0x0550
    elc = Elc(vid, pid, debug=0)
    return (elc, device)


def apply_action(elc, red, green, blue, duration, tempo, animation=AC_CHARGING, effect=COLOR):
    if (effect == COLOR):
        elc.remove_animation(animation)
        elc.start_new_animation(animation)
        elc.start_series(ZONES)
        # Static color, 2 second duration, tempo tempo (who cares?)
        elc.add_action((Action(effect, duration, tempo, red, green, blue),))
        elc.finish_save_animation(animation)
        elc.set_default_animation(animation)
    else:  # Then, effect is morph.
        elc.remove_animation(animation)
        elc.start_new_animation(animation)
        elc.start_series(ZONES)
        elc.add_action((Action(MORPH, duration, tempo, red, green, blue), Action(MORPH, duration, tempo, green,
                       blue, red), Action(MORPH, duration, tempo, blue, red, green)))  # Morph based on given values.
        elc.finish_save_animation(animation)
        elc.set_default_animation(animation)


def battery_flashing(elc):
    # Red flashing on battery low.
    elc.remove_animation(DC_LOW)
    elc.start_new_animation(DC_LOW)
    elc.start_series(ZONES)
    # Static color, 2 second duration, tempo tempo (who cares?)
    elc.add_action(
        (Action(COLOR, DURATION_BATTERY_LOW, TEMPO_MIN, 255, 0, 0),))
    # Static color, 2 second duration, tempo tempo (who cares?)
    elc.add_action((Action(COLOR, DURATION_BATTERY_LOW, TEMPO_MIN, 0, 0, 0),))
    elc.finish_save_animation(DC_LOW)
    elc.set_default_animation(DC_LOW)


def set_static(red, green, blue):
    elc, device = init_device()
    apply_action(elc, 0, 0, 0, DURATION_MAX, TEMPO_MIN,
                 AC_SLEEP, COLOR)       # Off on AC Sleep
    apply_action(elc, red, green, blue, DURATION_MAX, TEMPO_MIN,
                 AC_CHARGED, COLOR)     # Full brightness on AC, charged
    apply_action(elc, red, green, blue, DURATION_MAX, TEMPO_MIN,
                 AC_CHARGING, COLOR)    # Full brightness on AC, charging
    apply_action(elc, 0, 0, 0, DURATION_MAX, TEMPO_MIN,
                 DC_SLEEP, COLOR)       # Off on DC Sleep
    apply_action(elc, int(red/2), int(green/2), int(blue/2), DURATION_MAX, TEMPO_MIN,
                 DC_ON, COLOR)          # Half brightness on Battery
    battery_flashing(elc)  # Red flashing on battery low.
    apply_action(elc, 0, 0, 0, 0, 0,
                 DEFAULT_POST_BOOT, COLOR)       # Off on post-boot
    apply_action(elc, 0, 0, 0, 0, 0,
                 RUNNING_START, COLOR)           # Off on start
    apply_action(elc, 0, 0, 0, 0, 0,
                 RUNNING_FINISH, COLOR)          # Off on finish
    device.reset()


def set_morph(red, green, blue, duration):
    elc, device = init_device()
    apply_action(elc, 0, 0, 0, DURATION_MAX, TEMPO_MIN,
                 AC_SLEEP, COLOR)       # Off on AC Sleep
    apply_action(elc, red, green, blue, duration, TEMPO_MIN,
                 AC_CHARGED, MORPH)     # Full brightness on AC, charged
    apply_action(elc, red, green, blue, duration, TEMPO_MIN,
                 AC_CHARGING, MORPH)    # Full brightness on AC, charging
    apply_action(elc, 0, 0, 0, DURATION_MAX, TEMPO_MIN,
                 DC_SLEEP, COLOR)       # Off on DC Sleep
    apply_action(elc, int(red/2), int(green/2), int(blue/2), duration, TEMPO_MIN,
                 DC_ON, MORPH)          # Half brightness on Battery
    battery_flashing(elc)  # Red flashing on battery low.
    apply_action(elc, 0, 0, 0, 0, 0,
                 DEFAULT_POST_BOOT, COLOR)       # Off on post-boot
    apply_action(elc, 0, 0, 0, 0, 0,
                 RUNNING_START, COLOR)           # Off on start
    apply_action(elc, 0, 0, 0, 0, 0,
                 RUNNING_FINISH, COLOR)          # Off on finish
    device.reset()