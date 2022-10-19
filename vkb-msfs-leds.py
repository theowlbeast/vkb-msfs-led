from SimConnect import *
import logging
from SimConnect.Enum import *
from time import sleep
from datetime import datetime
import signal
import readchar

from vkb.devices import find_all_vkb
from vkb import led

import pygame

pygame.init()

def main():

    def led_reset():
        for led_key, led_ref in VKB_AV_LedRefMap.items() :
            if   0 != len(led_ref) :
                led_cfg = led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000')
                VKB_LedCfgData.append(led_cfg)
                VKB_LedStatus[led_key] = led_cfg

        for led_key, led_ref in VKB_SEM_LedRefMap.items() :
            if   0 != len(led_ref) :
                led_cfg = led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000')
                VKB_LedCfgData.append(led_cfg)
                VKB_LedStatus[led_key] = led_cfg

        vkb_inst.update_leds(VKB_LedCfgData)

    def handler(signum, frame):
        msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
        print(msg, end="", flush=True)
        res = readchar.readchar()
        if res == 'y':
            print("")
            led_reset()
            exit(1)
        else:
            print("", end="\r", flush=True)
            print(" " * len(msg), end="", flush=True) # clear the printed line
            print("    ", end="\r", flush=True)



    vkb_inst = find_all_vkb()[0]
    
    logging.basicConfig(level=logging.DEBUG)
    LOGGER = logging.getLogger(__name__)
    LOGGER.info("START")
    
    clock = pygame.time.Clock()
    
    sm = SimConnect()
    aq = AircraftRequests(sm)
    ae = AircraftEvents(sm)

    joysticks = {}
    sem_joy = {}

    engine_selector = {12:0,13:1,14:2,15:3} # SEM button index (SEM button num - 1) : engine index from GEN_MODE (starting 0)
    sem_guid = '030000001d2300002422000000000000' # SEM module GUID (VKBSim NXT SEM THQx2 FSM.GA)
    PG_Engine = 0
    
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
        ######## Avionics Master ########
        0   :   'AVIONICS_MASTER_SWITCH',                  #

        ######## AutoPilot Master ########
        1   :   'AUTOPILOT_MASTER',                        #
        2   :   'AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE',        #
        3   :   'AUTOPILOT_YAW_DAMPER',                    #

        ######## Landing Gear ########
        10  :   'GEAR_LEFT_POSITION',                      #
        11  :   'GEAR_CENTER_POSITION',                    #
        12  :   'GEAR_RIGHT_POSITION',                     #

        15  :   'BRAKE_PARKING_POSITION',                  #
        16  :   'TAILHOOK_POSITION',
        17  :   'WATER_RUDDER_HANDLE_POSITION',    


        ######## Autopilot Function ########
        18  :   'AUTOPILOT_WING_LEVELER',                  # LVL     
        19  :   'AUTOPILOT_PITCH_HOLD',                    # PIT
        20  :   'AUTOPILOT_ATTITUDE_HOLD',                 # ROL
        21  :   'AUTOPILOT_HEADING_LOCK',                  # HDG Const G X
        22  :   'AUTOPILOT_VERTICAL_HOLD',                 # VS  Const G X
        23  :   'AUTOPILOT_FLIGHT_LEVEL_CHANGE',           # FLC Const G X
        24  :   'AUTOPILOT_ALTITUDE_LOCK',                 # ALT Const G X
        25  :   'AUTOPILOT_ALTITUDE_ARM',                  # ALT Const Y X ; seems no use
        26  :   'AUTOPILOT_NAV1_LOCK',                     # NAV Const Y ? (Lo Prio)
        27  :   'AUTOPILOT_APPROACH_CAPTURED',             # NAV Const G X
        28  :   'AUTOPILOT_APPROACH_ACTIVE',               # NAV Const Y X (Hi Prio)
        29  :   'AUTOPILOT_APPROACH_ARM',                  # APR Const Y X ; seems no use
        30  :   'AUTOPILOT_GLIDESLOPE_HOLD',               # APR Const G X (Lo Prio)
        31  :   'AUTOPILOT_GLIDESLOPE_ARM',                # APR Const Y X
        32  :   'AUTOPILOT_GLIDESLOPE_ACTIVE',             # APR Const G X
        33  :   'AUTOPILOT_BACKCOURSE_HOLD',               # TRK / BCT

        40  :   'GENERAL_ENG_MASTER_ALTERNATOR:1',
        41  :   'GENERAL_ENG_MASTER_ALTERNATOR:2',
        42  :   'GENERAL_ENG_MASTER_ALTERNATOR:3',
        43  :   'APU_GENERATOR_SWITCH',

        45  :   'FUEL_TANK_SELECTOR:1',
        46  :   'FUEL_TANK_SELECTOR:2',


        50  :   'AUTOPILOT_ALTITUDE_LOCK_VAR'             # ALT seclet, not used
    }

    ################################
    # Simvar data update every cycle
    ################################
    SC_SimvarData = {}
    

    ################################
    # VKB LED reference map
    ################################
    VKB_AV_LedRefMap = {
        LED_FSM_AP: [1],
        LED_FSM_FD: [2],
        LED_FSM_YD: [3],
        LED_FSM_VS: [22],
        LED_FSM_L1: [21],                                           # HDG
        LED_FSM_L2: [33],                                           # TRK / BCT
        LED_FSM_L3: [18, 20, 21, 26, 27, 28],                       # NAV
        LED_FSM_L4: [28, 30, 31, 32],                               # APR
        LED_FSM_R1: [22, 23, 24, 25],                               # ALT
        LED_FSM_R2: [18],                                           # LVL
        LED_FSM_R3: [],                                             # VNV, NOP
        LED_FSM_R4: [23]                                           # FLC
    }

    VKB_SEM_LedRefMap = {
        LED_SEM_A1: [45],                                    # Fuel tank 1 selector
        LED_SEM_A2: [46],                                    # Fuel tank 2 selector
        LED_SEM_B1: [0],                                     # Avionics MASTER
        LED_SEM_B2: [40, 41, 42, 43],                        # Alernators / Generators
        LED_SEM_B3: [16, 17],                                # Water rudder / Tail hook
        LED_SEM_GL: [10, 15],
        LED_SEM_GF: [11, 15],
        LED_SEM_GR: [12, 15] 
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

    led_reset()
    
    signal.signal(signal.SIGINT, handler)




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

        # Add, delete and operate with any game device (joystick etc)
        for event in pygame.event.get():

            # if event.type == pygame.JOYBUTTONDOWN:
            #     # print("Joystick button pressed.")
            #     if event.button == 0:
            #         joystick = joysticks[event.instance_id]

            # if event.type == pygame.JOYBUTTONUP:
                # print("Joystick button released.")

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                # print(f"Joystick {event.instance_id} disconnected")

        # Get count of joysticks.
        joystick_count = pygame.joystick.get_count()

        # For each joystick:
        for joystick in joysticks.values():
            jid = joystick.get_instance_id()

            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()

            guid = joystick.get_guid()
            
            # Finding SEM module
            if joystick.get_guid() == sem_guid:
                sem_joy = joystick

            # power_level = joystick.get_power_level()

            # # Usually axis run in pairs, up/down for one, and left/right for
            # # the other. Triggers count as axes.
            # axes = joystick.get_numaxes()

            # for i in range(axes):
            #     axis = joystick.get_axis(i)

            # buttons = joystick.get_numbuttons()

            # for i in range(buttons):
            #     button = joystick.get_button(i)

            # hats = joystick.get_numhats()

            # # Hat position. All or nothing for direction, not a float like
            # # get_axis(). Position is a tuple of int values (x, y).
            # for i in range(hats):
            #     hat = joystick.get_hat(i)

        # Read MODE switch state from SEM
        for b,m in engine_selector.items():
            if sem_joy.get_button(b) == 1:
                PG_Engine = m
            # print(f'Selected engine: {engine}')
            # print(f'Selected source: {ledmap[GEN_MODE][engine]}')
            # print(f'Previous engine: {previous_engine}')

        # Clear cfg data
        VKB_LedCfgData = []

        # update simvars from MSFS
        for sc_key, sc_ref in SC_SimvarRefMap.items() :
            if   None != aq.find(sc_ref) :
                SC_SimvarData[sc_key] = aq.find(sc_ref).get()
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

            for led_key, led_ref in VKB_AV_LedRefMap.items() :

                # LED control disabled:
                if   0 == len(led_ref) :
                    None

                ################################
                # LED control custom logic:
                ################################

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
                        led_l4_mode = led.LEDMode.SLOW_BLINK

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
            for led_key, led_ref in VKB_AV_LedRefMap.items():
                if   0 != len(led_ref):
                    VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
        

        ################################
        # Working with AV independent LEDs
        ################################
        for led_key, led_ref in VKB_SEM_LedRefMap.items() :

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
                
                # Fuel tank selector
                elif LED_SEM_A1 == led_key :
                    if   20.0 == SC_SimvarData[led_ref[0]] : # fuel tank left main crossfeed to right main
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.SLOW_BLINK, '#444', '#fff'))
                    elif 19.0 == SC_SimvarData[led_ref[0]] : # fuel tank left main
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                    else : # off or other state
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#000', '#fff'))

                elif LED_SEM_A2 == led_key :
                    if   19.0 == SC_SimvarData[led_ref[0]] : # fuel tank right main crossfeed to left main
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.SLOW_BLINK, '#444', '#fff'))
                    elif 20.0 == SC_SimvarData[led_ref[0]] : # fuel tank right main
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                    else : # off or other state
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#000', '#fff'))

                # Water rudder / Tail hook
                elif LED_SEM_B3 == led_key :
                    if   (0.0 == SC_SimvarData[led_ref[0]]) and (-1.0 == SC_SimvarData[led_ref[1]]) : # tail hook is up no water rudder
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#000', '#fff'))
                    elif (0.0 == SC_SimvarData[led_ref[0]]) and (0.0 == SC_SimvarData[led_ref[1]]) : # water rudder is up no tail hook
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#000', '#fff'))
                    elif (1.0 == SC_SimvarData[led_ref[0]]) or (1.0 == SC_SimvarData[led_ref[1]]) : # water rudder or tail hook is down
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                    else : # off or other state
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1_p_2, led.LEDMode.FAST_BLINK, '#444', '#fff'))

                # Generator / alternator - use MODE switch on SEM for selecting of unit to display state (1: gen 1, 2: gen 2, 3: gen 3, 4: APU gen)
                elif LED_SEM_B2 == led_key :
                    if 1.0 == SC_SimvarData[led_ref[PG_Engine]]: # generator on
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))
                        gen_led_state='GREEN'
                    elif 0.0 == SC_SimvarData[led_ref[PG_Engine]]: # generator off
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR2, led.LEDMode.CONSTANT, '#000', '#fff'))
                        gen_led_state='RED'
                    else:
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
                        gen_led_state='OFF'
                    
                    # print(f'Selected source: {SC_SimvarRefMap.get(VKB_SEM_LedRefMap.get(led_key)[PG_Engine])} value: {SC_SimvarData[led_ref[PG_Engine]]} LED state: {gen_led_state}')
                
                elif 1 == len(led_ref) :
                    if   0.0 == SC_SimvarData[led_ref[0]]: # Disabled.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.OFF, '#000', '#000'))
                    else : # Enabled.
                        VKB_UpdateLedCfgData(led.LEDConfig(led_key, led.ColorMode.COLOR1, led.LEDMode.CONSTANT, '#777', '#000'))

        ################################
        # Finally write all changes to device
        ################################ 
        if VKB_LedCfgData:
            vkb_inst.update_leds(VKB_LedCfgData)

            # Clear cfg data (again)
            VKB_LedCfgData = []

        # sleep(0.2)
        # clock.tick(15)
    exit(1)
        

if __name__ == "__main__":
    main()
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()