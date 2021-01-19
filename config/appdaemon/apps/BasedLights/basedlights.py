import appdaemon.plugins.hass.hassapi as hass
import globals

class BasedLights(hass.Hass):
    def initialize(self):
        self.listen_state_handle_list = []
        self.appswitch = globals.get_arg(self.args, "app_switch")
        self.adaptive = globals.get_arg(self.args, "adaptive_light")
        self.nightmode = globals.get_arg(self.args, "nightmode")
        try: 
            self.night_scene = globals.get_arg(self.args, "night_scene")
            self.log("night_scene set to "+str(self.night_scene))
        except: 
            self.night_scene = None
            self.log("No night_scene set!")
        try: 
            self.switches = globals.get_arg(self.args, "switches")
            self.log("Switch set to "+str(self.switches))
        except: 
            self.switches = None
            self.log("No Switches set!")
        try: 
            self.lights_brightness = globals.get_arg(self.args, "lights_brightness")
            self.log("Lights Brightness set to "+str(self.lights_brightness))
        except: 
            self.lights_brightness = None
            self.log("No Lights Brightness set!")
        try: 
            self.lights_color_temp = globals.get_arg(self.args, "lights_color_temp")
            self.log("Lights Color Temp. set to "+str(self.lights_color_temp))
        except:
            self.lights_color_temp = None
            self.log("No Lights Color Temp. set!")
        try:
            self.lights_color_rgb = globals.get_arg(self.args, "lights_color_rgb")
            self.log("Lights RGB set to "+str(self.lights_color_rgb))
        except: 
            self.lights_color_rgb = None
            self.log("No Lights RGB set!")
        try:
            self.motion_sensor = globals.get_arg(self.args, "motion_sensor")
            self.log("Motion sensor set to  "+self.motion_sensor)
        except:
            self.motion_sensor = None
            self.log("No Motion Sensor set!")
        try:
            self.baynesian_sensor = globals.get_arg(self.args, "baynesian_sensor")
            self.log("Baynesian Sensor set to "+self.baynesian_sensor)
        except: 
            self.baynesian_sensor = None
            self.log("No Baynesian Sensor set!")
        try: 
            self.brightness_sensor = globals.get_arg(self.args, "brightness_sensor")
            self.log("Brightness Sensor set to "+self.brightness_sensor)
        except: 
            self.brightness_sensor = None
            self.log("No Brightness Sensor set!")
        try:
            self.brightness_value = globals.get_arg(self.args, "brightness_value")
            self.log("Brightness Value set to "+str(self.brightness_value))
        except: 
            self.brightness_value = None
            self.log("No Brightness Value set!")
        try:
            self.off_scene = globals.get_arg(self.args, "off_scene")
            self.log("Off Scene set to "+str(self.off_scene))
        except: 
            self.off_scene = None
            self.log("No Off Scene Value set!")
        try:
            self.on_scene = globals.get_arg(self.args, "on_scene")
            self.log("On Scene Value set to "+str(self.on_scene))
        except: 
            self.on_scene = None
            self.log("No On Scene Value set!")

        if self.motion_sensor != None:
            self.listen_state_handle_list.append(
                self.listen_state(self.listen_motion, self.motion_sensor)
            )
        if self.baynesian_sensor != None:
            self.listen_state_handle_list.append(
                self.listen_state(self.listen_baynesian, self.baynesian_sensor)
            )
        self.listen_state_handle = None

    def listen_baynesian(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.appswitch) == "on":
            if old != new:
                self.log(self.baynesian_sensor +" changed from "+ old +" to "+ new)
                if new == 'on':
                    self.log("looking for lights to turn on ")
                    self.log("sensor "+ str(self.brightness_sensor))
                    if self.brightness_sensor != None and self.brightness_value != None: 
                        if float(self.get_state(self.brightness_sensor)) <= float(self.brightness_value):
                            self.log("Sensor: "+str(self.get_state(self.brightness_sensor))+" below "+str(self.brightness_value))
                            self.lights_turn_on(self)
                    else: 
                        self.lights_turn_on(self)
                elif new == 'off':
                    self.log("Looking for lights to turn off")
                    if self.motion_sensor == None or self.get_state(self.motion_sensor) == 'off':
                        self.lights_turn_off(self)
                    else:
                        self.log("Setting lights were blocked by "+ self.motion_sensor)

    def listen_motion(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.appswitch) == "on":
            if old != new:
                self.log(self.motion_sensor +" changed from "+ old +" to "+ new)
                if new == 'on':
                    self.log("Looking for lights to turn on")
                    if self.baynesian_sensor == None or self.get_state(self.baynesian_sensor) == 'on':
                        if self.brightness_sensor != None and self.brightness_value != None: 
                            if float(self.get_state(self.brightness_sensor)) <= float(self.brightness_value):
                                self.log("Sensor: "+str(self.get_state(self.brightness_sensor))+" below "+str(self.brightness_value))
                                self.lights_turn_on(self)
                        else:
                            self.lights_turn_on(self)
                    else: 
                        self.log("Setting lights were blocked by "+ self.baynesian_sensor)
                elif new == 'off':
                    self.log("Looking for lights to turn off")
                    self.log(str(self.baynesian_sensor) +" "+ str(self.get_state(self.baynesian_sensor)))
                    if self.baynesian_sensor == None or self.get_state(self.baynesian_sensor) == 'off':
                        self.lights_turn_off(self)
                    else:
                        self.log("Setting lights were blocked by "+ self.baynesian_sensor)

    def lights_turn_on(self, kwargs):
        if self.get_state(self.nightmode) == 'off':
            if self.on_scene != None: 
                self.log("Turning on "+ str(self.on_scene))
                s = self.on_scene.split(".")
                self.log(""+str(s))
                self.call_service(
                    ""+s[0]+"/turn_on", entity_id = self.on_scene
                )
            else:
                if self.lights_color_rgb != None:
                    self.log("Turn on RGBs")
                    for light in self.lights_color_rgb:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct"), kelvin=self.get_state(self.adaptive, attribute="color_temp_kelvin")
                        )
                if self.lights_color_temp != None:
                    self.log("Turn on Color Temp")
                    for light in self.lights_color_temp:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct"), kelvin=self.get_state(self.adaptive, attribute="color_temp_kelvin")
                        )
                if self.lights_brightness != None:
                    self.log("Turn on Brightness Lights")
                    for light in self.lights_brightness:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct")
                        )
                        #"light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct")
                if self.switches != None:
                    self.log("Turn on Switches")
                    for light in self.switches:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "switch/turn_on", entity_id=light
                        )
        if self.get_state(self.nightmode) == 'on':
            if self.night_scene == None:
                if self.lights_color_rgb != None:
                    self.log("Turn on RGBs")
                    for light in self.lights_color_rgb:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct"), hs_color=self.get_state(self.adaptive, attribute="hs_color")
                        )
                if self.lights_color_temp != None:
                    self.log("Turn on Color Temp")
                    for light in self.lights_color_temp:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct"), kelvin=self.get_state(self.adaptive, attribute="color_temp_kelvin")
                        )
                if self.lights_brightness != None:
                    self.log("Turn on Brightness Lights")
                    for light in self.lights_brightness:
                        self.log("Turning on "+ str(light))
                        self.call_service(
                            "light/turn_on", entity_id=light, brightness_pct=self.get_state(self.adaptive, attribute="brightness_pct")
                        )
            else: 
                self.call_service(
                    "scene/turn_on", entity_id=self.night_scene
                )

    def lights_turn_off(self, kwargs):
        if self.off_scene != None: 
            self.log("Turning off "+ str(self.off_scene))
            self.call_service(
                "scene/turn_on", entity_id = self.off_scene
            )
        else:
            if self.lights_color_rgb != None:
                self.log("Turn off RGBs")
                for light in self.lights_color_rgb:
                    self.log("Turning off "+ str(light))
                    self.call_service(
                        "light/turn_off", entity_id=light
                    )
            if self.lights_color_temp != None:
                self.log("Turn off Color Temp")
                for light in self.lights_color_temp:
                    self.log("Turning off "+ str(light))
                    self.call_service(
                        "light/turn_off", entity_id=light
                    )
            if self.lights_brightness != None:
                self.log("Turn off Brightness")
                for light in self.lights_brightness:
                    self.log("Turning off "+ str(light))
                    self.call_service(
                        "light/turn_off", entity_id=light
                    )
            if self.switches != None:
                self.log("Turn off Switches")
                for light in self.switches:
                    self.log("Turning off "+ str(light))
                    self.call_service(
                        "switch/turn_off", entity_id=light
                    )

    def terminate(self):
        for listen_state_handle in self.listen_state_handle_list:
            self.cancel_listen_state(listen_state_handle)