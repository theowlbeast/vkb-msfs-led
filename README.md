# VKB FSM-GA LED bridge for MSFS

Steps to run:

1. Install [Python 3.8.11 Windows installer 64-bit](https://www.python.org/downloads/windows/) 
   (You can try other versions at your own risk!)
2. Install [Microsoft Visual C++ Build Tools](https://go.microsoft.com/fwlink/?LinkId=691126),
   choose "MSVC v140 - VS 2015 C++ build tools (v14.00)" and one of the 
   "Windows 10 SDK" (for building USB interface extensions)
3. clone `https://github.com/theowlbeast/pyvkb.git` and install `pyvkb` from source. (`python .\setup.py install`)
4. change to the directory you checked out this repository
5. run `python -m venv .`
6. run `python3 -m pip install -r requirements.txt`
7. run `python3 vkb-msfs-leds.py` after you started MSFS.

When you running `python3 -m pip install -r requirements.txt`, you may 
encounter `LINK : fatal error LNK1158: cannot run 'rc.exe'`. If this occurs, 
add Windows SDK bin directory to your path, like: `set PATH=C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64;%PATH%` 
(your Windows SDK version may be different, be sure to confirm it)

`RequestList.py` added some new datas in MSFS, namely `AUTOPILOT_ALTITUDE_ARM`, 
`AUTOPILOT_APPROACH_ARM`, `AUTOPILOT_APPROACH_ACTIVE`, `AUTOPILOT_APPROACH_CAPTURED`,
`AUTOPILOT_GLIDESLOPE_ARM` and `AUTOPILOT_GLIDESLOPE_ACTIVE`.

You'll need to use VKBDevCfg to change LED mode of all LEDs on FSM-GA to OFF, 
or they will behave erraticly (the program can't override LED presets defined 
with VKBDevCfg). They should show dim green after power up but not turn red 
when you push the buttons.

You may need to edit `vkb-msfs-leds.py` and change `FSM_LED_BASE` to the ID of 
first LED on your FSM-GA. It may differ depend on how you connect these modules. 
I have a SEM and it occupied led number 10-17. Check VkbDevCfg's 
Global -&gt; External -&gt; External Devices -&gt; FSM.GA and see the `Base` to the right 
ofr `LedsN`.
