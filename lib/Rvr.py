import asyncio
import os
import sys
import simpleaudio as sa
import math
import time

from sphero_sdk import SpheroRvrAsync
from sphero_sdk import Colors
from sphero_sdk import RvrLedGroups
from sphero_sdk import SerialAsyncDal
from sphero_sdk import DriveFlagsBitmask

class Rvr:
	colours = [ 0 ] * 10 * 3
	x = 32768
	y = 32768
	speed_scale = 2
	rvr = None

	def __init__( self, loop ):
		self.rvr = SpheroRvrAsync(
			dal=SerialAsyncDal(
				loop
			)
		)

	def is_top_left( self, x, y ):
		return x < 32768 and y < 32768

	def is_top_right( self, x, y ):
		return x >= 32768 and y < 32768

	def is_bottom_left( self, x, y ):
		return x < 32768 and y >= 32768

	def is_bottom_right( self, x, y ):
		return x >= 32768 and y >= 32768

	async def set_heading_speed( self, x, y ):
		ANALOG_MIN = 0
		ANALOG_CENTRE = 32768
		ANALOG_MAX = 65535
		STEPS = 32768 / 16

		if x == ANALOG_CENTRE and y == ANALOG_CENTRE:
			# Reset all driving
			await self.rvr.raw_motors( 0, 0, 0, 0 )
			return

		dist_x = max( abs( x - 32768 ), 1 )
		dist_y = max( abs( y - 32768 ), 1 )

		angle = math.degrees( math.atan( dist_y / dist_x ) )

		if self.is_top_left( x, y ):
			# Top left
			angle = 270 + angle
		elif self.is_bottom_left( x, y ):
			# Bottom left
			angle = 270 - angle
		elif self.is_top_right( x, y ):
			# Top right
			angle = 90 - angle
		elif self.is_bottom_right( x, y ):
			# Bottom right
			angle = 90 + angle

		# Calculate speed in 16 steps
		speed = math.sqrt( ( dist_x * dist_x ) + ( dist_y * dist_y ) )
		speed /= STEPS
		speed = int( round( speed, 0 ) )

		# Scale speed
		speed *= self.speed_scale

		# Set x,y values
		self.x = x
		self.y = y

		# RVR needs a whole degree
		angle = int( round( angle, 0 ) )

		await self.rvr.drive_with_heading(
			speed=speed,
			heading=angle,
			flags=DriveFlagsBitmask.none.value
		)

	def get_led_colour( self, led ):
		for position, group in enumerate(RvrLedGroups):
			if group.name != 'all_lights' and group.name != 'undercarriage_white' and ( group.name == led or led == 'all_lights' ):
				return self.colours[ position * 3 : ( position * 3 ) + 3 ]

	async def set_led_colour( self, led, rgb ):
		# can I just loop 0 to 10?
		for position, group in enumerate(RvrLedGroups):
			if group.name != 'all_lights' and group.name != 'undercarriage_white' and ( group.name == led or led == 'all_lights' ):
				self.colours[ ( position * 3 ) ] = rgb[ 0 ]
				self.colours[ ( position * 3 ) + 1 ] = rgb[ 1 ]
				self.colours[ ( position * 3 ) + 2 ] = rgb[ 2 ]

		copy = self.colours.copy()
		await self.rvr.set_all_leds(
			led_group=RvrLedGroups.all_lights.value,
			led_brightness_values=copy
		)

	async def set_led( self, options ):
		led = options["led"] if "led" in options else "all"
		colour = options["colour"] if "colour" in options else "255,0,0"
		rgb = list( map( int, colour.split( ',' ) ) )

		await self.set_led_colour( led, rgb )

	async def blink_led( self, options ):
		led = options["led"] if "led" in options else "all"
		blink = self.get_led_colour( led )

		await self.set_led_colour( led, [ 0, 0, 0 ] )
		await asyncio.sleep( 0.25 )
		await self.set_led_colour( led, blink )
		await asyncio.sleep( 0.25 )
		await self.set_led_colour( led, [ 0, 0, 0 ] )
		await asyncio.sleep( 0.25 )
		await self.set_led_colour( led, blink )

	async def reset( self ):
		await self.rvr.reset_yaw()
		await self.rvr.led_control.turn_leds_off()

		self.x = 32768
		self.y = 32768
		self.speed_scale = 2

	async def speed_increase( self ):
		 self.speed_scale = min( self.speed_scale + 1, 16 )

	async def speed_decrease( self ):
		 self.speed_scale = max( self.speed_scale - 1, 0 )

	async def drive_x( self, x ):
		await self.set_heading_speed( x, self.y )

	async def drive_y( self, y ):
		await self.set_heading_speed( self.x, y )

	async def play_sound( self, options ):
		sound = options["sound"] if "sound" in options else None

		if sound == None:
			return

		wave_obj = sa.WaveObject.from_wave_file( sound )
		play_obj = wave_obj.play()

	async def take_picture( self ):
		#filename = "images/rvr-%s" time.strftime("%H:%M:%S")
		camera = PiCamera()
		time.sleep(1)
		camera.capture(filename)

	async def do_action( self, action, options, value = None ):
		if action == "set_led":
			await self.set_led( options )
		elif action == "blink_led":
			await self.blink_led( options )
		elif action == "reset":
			await self.reset()
		elif action == "speed_increase":
			await self.speed_increase()
		elif action == "speed_decrease":
			await self.speed_decrease()
		elif action == "drive_x":
			await self.drive_x( value )
		elif action == "drive_y":
			await self.drive_y( value )
		elif action == "play_sound":
			await self.play_sound( options )
		elif action == "take_picture":
			await self.take_picture()

	async def close( self ):
		await self.rvr.close()

	async def run( self ):
		await self.rvr.wake()

		battery_percentage = await self.rvr.get_battery_percentage()
		print('Battery percentage: ', battery_percentage)

		await self.reset()
