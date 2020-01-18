#  RVR Bluetooth Joypad Control

Control a Sphero RVR with a bluetooth joypad controller. Configure actions for each gamepad button.

For example, use the analog stick to drive the RVR, use the main buttons to change colour, and the shoulder buttons to play a horn.

https://john.blog/2020/01/18/sphero-rvr-bluetooth-joypad/

https://videopress.com/v/GLNqxs8q

## Setup

You will need to mount a Raspberry Pi to your RVR and set up a Python environment. See Sphero's website for more details:

https://sdk.sphero.com/docs/getting_started/raspberry_pi/raspberry_pi_setup/

You will need the following Python libraries installed:

- sphero_sdk
- simpleaudio
- evdev

You will need to connect a bluetooth joypad to your Raspberry Pi using `bluetoothctl`.

## Configuration

Configuration is taken from the `rvr-joypad.json` file.

- `controller.device` - The joypad device
- `buttons` - Array of button configurations

Each button is configured as:

- `button` - The button name, taken from evdev
- `value` - The evdev value emitted when the button is pressed. Some buttons will emit different values. For example, a simple button is either 0 or 1. Analog buttons do not require a value
- `action` - The action to perform (see Actions)
- `options` - A JSON object containing options specific to the action

## Running

Start with:

`python rvr-joypad.py`

If everything is set up correctly you will then be able to control your RVR.

It is assumed that the RVR device will be driven using analog controls. This gives us an X and Y offset, as well as offset from the centre position. Using these values we can work out an angle and speed - the harder you push the analog stick, the faster it will go.

The speed is scaled to a maximum value. When first started this will be at the smallest value, and it can be adjusted with the `speed_increase` and `speed_decrease` values.

The RVR heading is determined by the start position of the RVR. That is, 'up' on the analog stick corresponds to forward in whichever direction the RVR is facing when first started.

If you wish to change this then you can issue the 'reset' action, which will reset the start position to wherever the RVR is currently facing. This is useful if you change your own position in relation to the RVR.

## Actions

The following actions are supported:

- `drive_x` - Change the RVR X direction by the analog value and direction
- `drive_y` - Change the RVR Y direction by the analog value and direction
- `speed_increase` - Increase speed scaling
- `speed_decrease` - Decrease speed scaling
- `play_sound` - Play a sound, if a sound device is attached and configured
- `reset` - Reset speed scaling and home direction
- `set_led` - Change the LED to a colour. `options` are:
  - `led` - The LED name, as defined in Sphero SDK. Can be `all_lights` for all LEDs
  - `colour` - RGB values in the format `R,G,B`. For example `255,0,0` is red.
- `nothing` - Do nothing
