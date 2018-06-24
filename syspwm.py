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

	chippath = "/sys/class/pwm/pwmchip0"

	def __init__(self,pwm):
		self.pwm=pwm
		self.pwmdir="{chippath}/pwm{pwm}".format(chippath=self.chippath,pwm=self.pwm)
		if not self.overlay_loaded():
			raise SysPWMException("Need to add 'dtoverlay=pwm-2chan' to /boot/config.txt and reboot")
		if not self.export_writable():
			raise SysPWMException("Need write access to files in '{chippath}'".format(chippath=self.chippath))
		if not self.pwmX_exists():
			self.create_pwmX()
		return

	def overlay_loaded(self):
		return os.path.isdir(self.chippath)

	def export_writable(self):
		return os.access("{chippath}/export".format(chippath=self.chippath), os.W_OK)

	def pwmX_exists(self):
		return os.path.isdir(self.pwmdir)

	def echo(self,m,fil):
		#print "echo {m} > {fil}".format(m=m,fil=fil)
		with open(fil,'w') as f:
			f.write("{m}\n".format(m=m))

	def create_pwmX(self):
		pwmexport = "{chippath}/export".format(chippath=self.chippath)
		self.echo(self.pwm,pwmexport)

	def enable(self,disable=False):
		enable = "{pwmdir}/enable".format(pwmdir=self.pwmdir)
		num = 1
		if disable:
			num = 0
		self.echo(num,enable)

	def disable(self):
		return self.enable(disable=True)

	def set_duty_cycle(self,milliseconds):
		# /sys/ iface, 2ms is 2000000
		# gpio cmd,    2ms is 200
		dc = int(milliseconds * 1000000)
		duty_cycle = "{pwmdir}/duty_cycle".format(pwmdir=self.pwmdir)
		self.echo(dc,duty_cycle)

	def set_frequency(self,hz):
		per = (1 / float(hz))
		per *= 1000    # now in milliseconds
		per *= 1000000 # now in.. whatever
		per = int(per)
		period = "{pwmdir}/period".format(pwmdir=self.pwmdir)
		self.echo(per,period)

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
