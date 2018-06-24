# syspwm
Python Libary for Hardware PWM on Raspberry Pi using Linux kernel driver and /sys interface 

This is a python library that allows control of the limited number of PWM pins available on most Raspberry Pi hardware. It does via a Linux kernel PWM driver that comes with recent kernels (at least version 4.9).

Using it to, for example, control servo motors leads to very smooth control, which I wasn't able to get with RPi.GPIO on a Raspberry Pi Zero W.

**Enabling PWM driver:**
1. Edit /boot/config.txt and add the following:  `dtoverlay=pwm-2chan`
1. Reboot
1. Check that driver is loaded: `lsmod | grep pwm_bcm`
    1. Output should be something like `pwm_bcm2835             2711  0`

**Using code:**

Place `syspwm.py` in the same directory as your code, and include it like `from syspwm import SysPWM`

The following code uses syspwm to  smoothly turn a servo through its turning radius. Tweak the duty cycle values of S, E, and M to cause your servo to go to its start, end, and middle positions, respectively.
````python
from syspwm import SysPWM
from time   import sleep
import sys,os
import atexit

SLEE=0.02
PAUS=2
FREQ=20

S=0.65
E=2.30
M=1.40

#pwm0 is GPIO pin 18 is physical pin 12
pwm = SysPWM(0)
pwm.set_frequency(FREQ)
pwm.set_duty_cycle(S)
atexit.register(pwm.disable)
pwm.enable()
sleep(PAUS)

intS = int(S*100)
intE = int(E*100)
while True:
        for i in range(intS,intE):
                pwm.set_duty_cycle(i/100.0)
                #print i-intS
                sleep(SLEE)
        sleep(PAUS)
        for i in range(intE,intS,-1):
                pwm.set_duty_cycle(i/100.0)
                #print i-intS
                sleep(SLEE)
        sleep(PAUS)
````
I learned the /sys interface for hardware PWM from http://www.jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html
