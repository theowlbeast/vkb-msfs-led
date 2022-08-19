from SimConnect import *
import logging
from SimConnect.Enum import *
from time import sleep

from vkb.devices import find_all_vkb
from vkb import led

ext = find_all_vkb()[0]

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.info("START")

sm = SimConnect()
aq = AircraftRequests(sm)
ae = AircraftEvents(sm)

### BEGIN THQ_SEM_FSM

LED_THQ_MD = 0

LED_SEM_A1 = 10
LED_SEM_A2 = 11
LED_SEM_B1 = 12
LED_SEM_B2 = 13
LED_SEM_B3 = 14

LED_SEM_GL = 15
LED_SEM_GF = 16
LED_SEM_GR = 17

LED_FSM_L1 = 18
LED_FSM_L2 = 19
LED_FSM_L3 = 20
LED_FSM_L4 = 21
LED_FSM_R1 = 22
LED_FSM_R2 = 23
LED_FSM_R3 = 24
LED_FSM_R4 = 25

LED_FSM_AP = 26
LED_FSM_FD = 27
LED_FSM_YD = 28
LED_FSM_VS = 29

### END THQ_SEM_FSM

FSM_LED_BASE = 18

APPR_LED = FSM_LED_BASE + 3
ALT_LED = FSM_LED_BASE + 4

ALT_MODE = 50
APPR_MODE = 51
GEAR_MODE = 52

SEM_LED_BASE = 10
GEAR_LED_BASE = SEM_LED_BASE + 5

# { led: simvar }
ledmap = {
    LED_FSM_L1: aq.find('AUTOPILOT_HEADING_LOCK'),
    LED_FSM_L3: aq.find('AUTOPILOT_NAV1_LOCK'),
    LED_FSM_L4: aq.find('AUTOPILOT_GLIDESLOPE_HOLD'),
    LED_FSM_R1: aq.find('AUTOPILOT_ALTITUDE_LOCK'),
    
    #FSM_LED_BASE + 2:  aq.find('AUTOPILOT_NAV1_LOCK'),
    LED_FSM_R4: aq.find('AUTOPILOT_FLIGHT_LEVEL_CHANGE'),
    LED_FSM_AP: aq.find('AUTOPILOT_MASTER'),
    LED_FSM_FD: aq.find('AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE'),
    LED_FSM_YD: aq.find('AUTOPILOT_YAW_DAMPER'),
    LED_FSM_VS: aq.find('AUTOPILOT_VERTICAL_HOLD'),

    # altitude
    
#    ALT_MODE: [
#        aq.find('AUTOPILOT_ALTITUDE_ARM'),
#        aq.find('AUTOPILOT_ALTITUDE_LOCK')],

    # approach
#    APPR_MODE: [
#        aq.find('AUTOPILOT_APPROACH_ARM'), # None
#        aq.find('AUTOPILOT_APPROACH_ACTIVE'),
#        aq.find('AUTOPILOT_APPROACH_CAPTURED'),
#        aq.find('AUTOPILOT_GLIDESLOPE_ARM'),
#        aq.find('AUTOPILOT_GLIDESLOPE_ACTIVE')],

    LED_SEM_GL: aq.find('GEAR_LEFT_POSITION'),
    LED_SEM_GF: aq.find('GEAR_CENTER_POSITION'),
    LED_SEM_GR: aq.find('GEAR_RIGHT_POSITION')
}

current_state = {}
previous_state = {}
led_config = []

# disable all leds
for k, v in ledmap.items():
    if k < 50:
        previous_state[k] = 5.0
        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
led_config.append(led.LEDConfig(LED_FSM_L3, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
led_config.append(led.LEDConfig(LED_FSM_L4, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
ext.update_leds(led_config)
sleep(1)

while not sm.quit:
    current_state = {}
    led_config = []
#    print(aq.find('AVIONICS_MASTER_SWITCH').get())
# ELECTRICAL_MASTER_BATTERY
    #print(aq.find('AVIONICS_MASTER_SWITCH').get())
    if 1.0 == aq.find('AVIONICS_MASTER_SWITCH').get():
        # enable led control
        #print("flush")
        for k, v in ledmap.items():
            if type(v) == list:
                current_state[k] = [w.get() for w in list(filter(None,v))]
            else:
                current_state[k] = v.get()

        for k, v in current_state.items():
            if v != previous_state.get(k):
                previous_state[k] = v

                if k == ALT_MODE:

                    if v == 1.0: # altitude lock
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                    else:
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                #    if v[1] == 1.0: # altitude lock
                #        led_config.append(led.LEDConfig(ALT_LED, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                #    elif v[0] == 1.0: # altitude arm
                #        led_config.append(led.LEDConfig(ALT_LED, led.ColorMode.COLOR1_p_2, led.LEDMode.CONSTANT, '#444', '#fff'))
                #    else:
                #        led_config.append(led.LEDConfig(ALT_LED, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))

                #elif k == APPR_MODE:
                #    if v[4] == 1.0: # glideslope active
                #        led_config.append(led.LEDConfig(APPR_LED, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                #    elif v[2] == 1.0 and v[3] == 1.0: # approach captured, glideslope arm
                #        led_config.append(led.LEDConfig(APPR_LED, led.ColorMode.COLOR1, led.LEDMode.SLOW_BLINK, '#fff', '#fff'))
                #    elif v[1] == 1.0: # approach active
                #        led_config.append(led.LEDConfig(APPR_LED, led.ColorMode.COLOR1_p_2, led.LEDMode.CONSTANT, '#444', '#fff'))
                #    elif v[0] == 1.0: # approach arm
                #        led_config.append(led.LEDConfig(APPR_LED, led.ColorMode.COLOR1_p_2, led.LEDMode.SLOW_BLINK, '#444', '#fff'))
                #    else:
                #        led_config.append(led.LEDConfig(APPR_LED, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                elif k == LED_FSM_L3: # NAV
                    if v == 1.0:
                        led_config.append(led.LEDConfig(LED_FSM_L3, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                        #led_config.append(led.LEDConfig(LED_FSM_L4, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                    else:
                        led_config.append(led.LEDConfig(LED_FSM_L3, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                        #led_config.append(led.LEDConfig(LED_FSM_L4, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                        
                elif k == LED_FSM_L4: # APPR
                    if v == 1.0:
                        led_config.append(led.LEDConfig(LED_FSM_L3, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                        led_config.append(led.LEDConfig(LED_FSM_L4, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                    else:
                        led_config.append(led.LEDConfig(LED_FSM_L3, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                        led_config.append(led.LEDConfig(LED_FSM_L4, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
                    
                    
                elif k >= LED_SEM_GL and k <= LED_SEM_GR:
                    if v == 0.0: # gear is up
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#fff', '#fff'))
                    elif v == 1.0: # gear is down
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                    else: # gear in transit
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1_p_2, led.LEDMode.FAST_BLINK, '#444', '#fff'))

                else:
                    # generic flag, 1.0 = BRIGHT GREEN LED, 0.0 = dim green led
                    if v == 1.0:
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#fff', '#fff'))
                    elif v == 0.0:
                        led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
        
    else:
        # disable all leds
        #print("close")
        for k, v in previous_state.items():
            if k < 50:
                previous_state[k] = 2.0
                led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
        led_config.append(led.LEDConfig(LED_FSM_L3, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
        led_config.append(led.LEDConfig(LED_FSM_L4, led.ColorMode.COLOR1, led.LEDMode.OFF, '#fff', '#fff'))
        
        #for k, v in ledmap.items():
        #    led_config.append(led.LEDConfig(k, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#000', '#000'))
        
    if led_config:
        ext.update_leds(led_config)

    sleep(0.2)
