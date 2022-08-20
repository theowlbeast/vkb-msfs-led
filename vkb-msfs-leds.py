from SimConnect import *
import logging
from SimConnect.Enum import *
from time import sleep

from vkb.devices import find_all_vkb
from vkb import led

vkb_inst = find_all_vkb()[0]

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

################################
# Simvar reference map
################################
SC_SimvarRefMap = {
    ######## AutoPilot Master ########
    0   :   aq.find('AUTOPILOT_MASTER'),                        #
    1   :   aq.find('AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE'),        #
    2   :   aq.find('AUTOPILOT_YAW_DAMPER'),                    #
    
    ######## Landing Gear ########
    10  :   aq.find('GEAR_LEFT_POSITION'),                      #
    11  :   aq.find('GEAR_CENTER_POSITION'),                    #
    12  :   aq.find('GEAR_RIGHT_POSITION'),                     #
    
    15  :   aq.find('BRAKE_PARKING_POSITION'),                  #
    
    ######## Autopilot Function ########
    18  :   aq.find('AUTOPILOT_WING_LEVELER'),                  # LVL     
    19  :   aq.find('AUTOPILOT_PITCH_HOLD'),                    # PIT
    20  :   aq.find('AUTOPILOT_ATTITUDE_HOLD'),                 # ROL
    21  :   aq.find('AUTOPILOT_HEADING_LOCK'),                  # HDG Const G X
    22  :   aq.find('AUTOPILOT_VERTICAL_HOLD'),                 # VS  Const G X
    23  :   aq.find('AUTOPILOT_FLIGHT_LEVEL_CHANGE'),           # FLC Const G X
    24  :   aq.find('AUTOPILOT_ALTITUDE_LOCK'),                 # ALT Const G X
    25  :   aq.find('AUTOPILOT_ALTITUDE_ARM'),                  # ALT Const Y X ; seems no use
    26  :   aq.find('AUTOPILOT_NAV1_LOCK'),                     # NAV Const Y ? (Lo Prio)
    27  :   aq.find('AUTOPILOT_APPROACH_CAPTURED'),             # NAV Const G X
    28  :   aq.find('AUTOPILOT_APPROACH_ACTIVE'),               # NAV Const Y X (Hi Prio)
    29  :   aq.find('AUTOPILOT_APPROACH_ARM'),                  # APR Const Y X ; seems no use
    30  :   aq.find('AUTOPILOT_GLIDESLOPE_HOLD'),               # APR Const G X (Lo Prio)
    31  :   aq.find('AUTOPILOT_GLIDESLOPE_ARM'),                # APR Const Y X
    32  :   aq.find('AUTOPILOT_GLIDESLOPE_ACTIVE'),             # APR Const G X
    
    50  :   aq.find('AUTOPILOT_ALTITUDE_LOCK_VAR'),             # ALT selet, not used
}

################################
# Simvar data update every cycle
################################
SC_SimvarData = {}

################################
# VKB LED reference map
################################
VKB_LedRefMap = {
    LED_FSM_AP: [0],
    LED_FSM_FD: [1],
    LED_FSM_YD: [2],
    LED_FSM_VS: [22],
    LED_FSM_L1: [21],                                           # HDG
    LED_FSM_L2: [],
    LED_FSM_L3: [18, 20, 21, 26, 27, 28],                       # NAV
    LED_FSM_L4: [28, 30, 31, 32],                               # APR
    LED_FSM_R1: [22, 23, 24, 25],                               # ALT
    LED_FSM_R2: [18],                                           # LVL
    LED_FSM_R3: [],                                             # VNV, NOP
    LED_FSM_R4: [23],                                           # FLC
    LED_SEM_GL: [10, 15],
    LED_SEM_GF: [11, 15],
    LED_SEM_GR: [12, 15], 
}


################################
# VKB LED status data, generate by logic
################################
VKB_LedCfgData = []

################################
# VKB LED update data, update every cycle
################################
VKB_LedStatus = {}

################################
# VKB LED initial config
# Disable all LEDs and record status
################################
for led_key, led_ref in VKB_LedRefMap.items() :
    if   0 != len(led_ref) :
        led_cfg = led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000')
        VKB_LedCfgData.append(led_cfg)
        VKB_LedStatus[led_key] = led_cfg
vkb_inst.update_leds(VKB_LedCfgData)


sleep(1)

################################
# Auto handle VKB LED update logic 
################################
def VKB_UpdateLedCfgData( led_cfg ) :
    if VKB_LedStatus[led_cfg.led] != led_cfg :
        VKB_LedCfgData.append(led_cfg)
        VKB_LedStatus[led_cfg.led] = led_cfg

################################
# Main loop begin
################################
while not sm.quit :
    
    # Clear cfg data
    VKB_LedCfgData = []
    
    # update simvars from MSFS
    for sc_key, sc_ref in SC_SimvarRefMap.items() :
        if   None != sc_ref :
            SC_SimvarData[sc_key] = sc_ref.get()
        else:
            print("[E] Simvar not found !")
    
    #print(aq.find('AVIONICS_MASTER_SWITCH').get())
    #ELECTRICAL_MASTER_BATTERY
    #print(aq.find('AVIONICS_MASTER_SWITCH').get())
    
    ################################
    # Only enable LEDs w/ avionics power
    ################################
    if   1.0 == aq.find('AVIONICS_MASTER_SWITCH').get():
        # enable led control
        #print("flush")
        
        for led_key, led_ref in VKB_LedRefMap.items() :
            
            # LED control disabled:
            if   0 == len(led_ref) :
                None
             
            ################################
            # LED control custom logic:
            ################################
            
            # Landing Gear
            elif (LED_SEM_GL <= led_key) & (LED_SEM_GR >= led_key) :
                if   0.0 == SC_SimvarData[led_ref[0]] : # gear is up
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#000', '#fff'))
                elif (1.0 == SC_SimvarData[led_ref[0]]) & (0.0 == SC_SimvarData[led_ref[1]]) : # gear is down, parking brake off
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                elif (1.0 == SC_SimvarData[led_ref[0]]) & (1.0 == SC_SimvarData[led_ref[1]]) : # gear is down, parking brake on
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.CONSTANT, '#444', '#fff'))
                else : # gear in transit
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.FAST_BLINK, '#444', '#fff'))
                
            # NAV
            elif LED_FSM_L3 == led_key :
                #print("NAV")
                #print(SC_SimvarData[led_ref[0]])
                #print(SC_SimvarData[led_ref[1]])
                #print(SC_SimvarData[led_ref[2]])
                
                if   (1.0 == SC_SimvarData[led_ref[3]]) | (1.0 == SC_SimvarData[led_ref[5]]) : # APR or NAV enabled.
                    if   1.0 == SC_SimvarData[led_ref[4]] : # NAV captured. #FIXME won't trigger, seems buggy.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
                    elif (1.0 == SC_SimvarData[led_ref[0]]) | (1.0 == SC_SimvarData[led_ref[1]]) | (1.0 == SC_SimvarData[led_ref[2]]) : # NAV armed, temporarily solution.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.CONSTANT, '#444', '#fff'))
                    else : # NAV captured. #FIXME will always trigger this one without temporarily solution.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                else : # NAV disabled.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
            
            # APR
            elif LED_FSM_L4 == led_key :
                #print("APR")
                #print(SC_SimvarData[led_ref[0]])
                #print(SC_SimvarData[led_ref[1]])
                #print(SC_SimvarData[led_ref[2]])
                #print(SC_SimvarData[led_ref[3]])
                
                # if GS enabled but APR not, blink this LED.
                led_l4_mode = led.LEDMode.CONSTANT
                if 0.0 == SC_SimvarData[led_ref[0]] :
                    led_mode = led.LEDMode.SLOW_BLINK
                    
                if  1.0 == SC_SimvarData[led_ref[1]] : # GS enabled.
                    if   1.0 == SC_SimvarData[led_ref[2]] : # GS armed.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led_l4_mode, '#444', '#fff'))
                    elif 1.0 == SC_SimvarData[led_ref[3]] : # GS captured.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led_l4_mode, '#777', '#000'))
                else : # GS disabled.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000')) 
                
            # ALT
            elif LED_FSM_R1 == led_key:
                #print("ALT")
                #print(SC_SimvarData[led_ref[0]])
                #print(SC_SimvarData[led_ref[1]])
                #print(SC_SimvarData[led_ref[2]])
                #print(SC_SimvarData[led_ref[3]])
                
                if   1.0 == SC_SimvarData[led_ref[3]] : # ATL armed, seems no effect. #FIXME If you see ALT blink yellow, plz report.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.SLOW_BLINK, '#444', '#fff'))
                elif (1.0 == SC_SimvarData[led_ref[0]]) | (1.0 == SC_SimvarData[led_ref[1]]) : # ALT armed, temporarily solution.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.CONSTANT, '#444', '#fff'))
                elif 1.0 == SC_SimvarData[led_ref[2]] : # ALT captured.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                else : # ALT disabled.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
            
            # LED control direct map:
            elif 1 == len(led_ref) :
                if   0.0 == SC_SimvarData[led_ref[0]]: # Disabled.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
                else : # Enabled.
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))

    ################################
    # Disable all LEDs w/o avionics power
    ################################ 
    else:
        for led_key, led_ref in VKB_LedRefMap.items():
            if   0 != len(led_ref):
                VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
    
    ################################
    # Finally write all changes to device
    ################################ 
    if VKB_LedCfgData:
        vkb_inst.update_leds(VKB_LedCfgData)
        
        # Clear cfg data (again)
        VKB_LedCfgData = []

    # sleep(0.2)
