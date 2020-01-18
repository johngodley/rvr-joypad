import asyncio
import json

from lib.Joypad import Joypad
from lib.Rvr import Rvr

async def main( pad, rover ):
	await rover.run()
	await pad.run( rover )

loop = asyncio.get_event_loop()

if __name__ == '__main__':
	try:
		with open( 'rvr-joypad.json', 'r' ) as json_file:
			config = json.load( json_file )

		rover = Rvr( loop )
		joypad = Joypad( config["buttons"], config["controller"]["device"] )

		loop.run_until_complete( main( joypad, rover ) )

	except KeyboardInterrupt:
		print('\nProgram terminated with keyboard interrupt.')

		loop.run_until_complete(
			rover.close()
		)

	except FileNotFoundError:
		print('Controller not detected')

	finally:
		if loop.is_running():
			loop.close()
