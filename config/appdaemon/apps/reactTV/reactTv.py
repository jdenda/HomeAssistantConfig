import appdaemon.plugins.hass.hassapi as hass
import globals

class ReactTv(hass.Hass):
    def initialize(self):
        self.listen_state_handle_list = []

        self.media_player = globals.get_arg(self.args, "media_player")
        self.motion = globals.get_arg(self.args, "motion")
        self.nightmode = globals.get_arg(self.args, "nightmode")
        self.adaptive_light = globals.get_arg(self.args, "adaptive_light")
        self.scene_movie = globals.get_arg(self.args, "scene_movie")
        self.lights = globals.get_arg(self.args, "lights")
        self.scene_normal = globals.get_arg(self.args, "script_normal")
        self.scene_night = globals.get_arg(self.args, "scene_night")
        self.scene_movie_paused = globals.get_arg(self.args, "scene_movie_paused")
        self.appswitch = globals.get_arg(self.args, "appswitch")
        self.besuch = globals.get_arg(self.args, "besuch")

        self.listen_state_handle_list.append(
            self.listen_state(self.state_change, self.media_player)
        )

    def state_change(self, entity, attribute, old, new, kwargs):
        if (old != new) and (self.get_state(self.appdswitch) == "on") and (self.get_state(self.besuch) == "off"):
            self.log("changed from "+str(old)+" to "+str(new))
            if (new == "playing"):
                self.call_service(
                    "switch/turn_off", entity_id=self.adaptive_light
                )
                self.call_service(
                    "scene/turn_on", entity_id=self.scene_movie
                )
            elif (new == "paused"):
                self.call_service(
                    "switch/turn_off", entity_id=self.adaptive_light
                )
                self.call_service(
                    "scene/turn_on", entity_id=self.scene_movie_paused
                )
            elif (new == "idle"):
                self.call_service(
                    "switch/turn_on", entity_id=self.adaptive_light
                )
                self.select_scene(new)
            elif (new == "off"):
                self.call_service(
                    "switch/turn_on", entity_id=self.adaptive_light
                )
                self.select_scene(new)
            else: 
                self.log("no match found")

    def select_scene(self, new):
        self.log("selecting scene")
        if (self.get_state(self.nightmode) == "on"):
            self.call_service(
                "scene/turn_on", entity_id=self.scene_night
            )
        else:
            self.call_service(
                "script/turn_on", entity_id=self.scene_normal
            )