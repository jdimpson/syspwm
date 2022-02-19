#!/usr/bin/env python
import os.path

# Copyright 2018 Jeremy Impson <jdimpson@acm.org>

# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free 
# Software Foundation; either version 3 of the License, or (at your option) 
# any later version.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses>.

class SysPWMException(Exception):
	pass

# /sys/ pwm interface described here: http://www.jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html
class SysPWM(object):

        __chippath = "/sys/class/pwm/pwmchip0"
        __pwm = None
        __pwmdir = None
        __period_ns = 0
        __frequency_hz = 0
        __duty_cycle = 0

        def __init__(self,pwm,frequency):
                self.__pwm=pwm
                self.__pwmdir="{chippath}/pwm{pwm}".format(chippath=self.__chippath,pwm=self.__pwm)
                if not self.overlay_loaded():
                        raise SysPWMException("Need to add 'dtoverlay=pwm-2chan' to /boot/config.txt and reboot")
                if not self.export_writable():
                        raise SysPWMException("Need write access to files in '{chippath}'".format(chippath=self.__chippath))
                if not self.pwmX_exists():
                        self.create_pwmX()
                self.set_frequency(frequency)
                return

        def overlay_loaded(self):
                return os.path.isdir(self.__chippath)

        def export_writable(self):
                return os.access("{chippath}/export".format(chippath=self.__chippath), os.W_OK)

        def pwmX_exists(self):
                return os.path.isdir(self.__pwmdir)

        def echo(self,m,fil):
                #print "echo {m} > {fil}".format(m=m,fil=fil)
                with open(fil,'w') as f:
                        f.write("{m}\n".format(m=m))

        def create_pwmX(self):
                pwmexport = "{chippath}/export".format(chippath=self.__chippath)
                self.echo(self.__pwm,pwmexport)

        def enable(self,disable=False):
                enable = "{pwmdir}/enable".format(pwmdir=self.__pwmdir)
                num = 1
                if disable:
                        num = 0
                self.echo(num,enable)

        def disable(self):
                return self.enable(disable=True)

        def set_duty_cycle(self,duty_cycle):
                self.__duty_cycle = max(0, min(1, duty_cycle))
                duty_cycle_ns = int(self.__duty_cycle*self.__period_ns)
                path = "{pwmdir}/duty_cycle".format(pwmdir=self.__pwmdir)
                self.echo(duty_cycle_ns, path)

        def set_frequency(self,frequency):
                old_dc = self.__duty_cycle
                self.set_duty_cycle(0)

                self.__frequency = int(frequency)
                self.__period_ns = int((1.0/self.__frequency)*1e9)

                self.set_duty_cycle(old_dc)
                path = "{pwmdir}/period".format(pwmdir=self.__pwmdir)
                self.echo(self.__period_ns,path)

if __name__ == "__main__":
	from time import sleep
	import atexit
	SLEE=3
	FREQ=20
	# Tinkerkit
	S=0.50
	E=2.30
	M=1.40
	# Tower ProMG996R
	#S=0.46
	#E=2.54
	#M=1.50

	#pwm0 is GPIO pin 18 is physical pin 12
	pwm = SysPWM(0)
	pwm.set_frequency(FREQ)
	pwm.set_duty_cycle(S)
	atexit.register(pwm.disable)
	pwm.enable()

	while True:
		pwm.set_duty_cycle(S)
		print 0
		sleep(SLEE)
		pwm.set_duty_cycle(M)
		print 90
		sleep(SLEE)
		pwm.set_duty_cycle(E)
		print 180
		sleep(SLEE)
