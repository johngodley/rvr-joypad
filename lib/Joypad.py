from evdev import InputDevice, categorize, ecodes

class Joypad:
	buttons = []
	joypad = None

	def __init__( self, buttons, device ):
		self.buttons = buttons
		self.joypad = InputDevice( device )

	async def do_button( self, button, value, rover ):
		options = button["options"] if "options" in button else None

		if "value" in button:
			if value == button["value"]:
				await rover.do_action( button["action"], options )
		else:
			await rover.do_action( button["action"], options, value )

	async def run( self, rover ):
		for ev in self.joypad.async_read_loop():
			event = categorize( ev )

			if ev.type == ecodes.EV_KEY or ev.type == ecodes.EV_ABS:
				for button in self.buttons:
					if ev.code == ecodes.ecodes[ button["button"] ]:
						await self.do_button( button, ev.value, rover )
