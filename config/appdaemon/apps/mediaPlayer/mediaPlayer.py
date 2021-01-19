import appdaemon.plugins.hass.hassapi as hass
import datetime
import globals
import time 

class MediaPlayerStartPlayback(hass.Hass):
    def initialize(self):
        self.timer_handle_list = []
        self.check_devices = "sensor.chromecast_devices"
        # self.notifier = self.get_app("Notifier")

    def play(self, playlist, destination, bug_notifier):
        if self.get_state(self.check_devices) == "ok":
            self.log("Set Playlist to {}".format(playlist))
            try: 
                self.call_service("input_select/select_option", entity_id="input_select.playlists", option=playlist)
            except:
                # self.notifier.notify("{}".format(bug_notifier), "Konnte Werte für die Playlist nicht setzen.")   
                self.log("Konnte Werte für die Playlist nicht setzen.") 
            self.log("Set Destination to {}".format(destination))
            try:
                self.call_service("input_select/select_option", entity_id="input_select.playback_devices", option=destination)
            except:
                # self.notifier.notify("{}".format(bug_notifier), "Konnte Werte für die Wiedergabegeräte nicht setzen.")   
                self.log("Konnte Werte für die Wiedergabegeräte nicht setzen.") 
            self.log("Start Script")
            # try:
            try:
                self.call_service("script/cf_start_playback")
            except TimeoutError:
                self.log("timeouterror starting playback, can be ignored") 
            # except:
            #     self.notifier.notify("{}".format(bug_notifier), "Konnte Script nicht ausführen.")   
            #     self.log("Konnte Script nicht ausführen.") 

        else:
            # self.notifier.notify(bug_notifier, "Chromecast/Spotcast ist nicht erreichbar.")
            self.log("Chromecast/Spotcast ist nicht erreichbar.")


class MediaPlayerAdjust(hass.Hass):
    def initialize(self):
        self.timer_handle = None
        self.listen_event_handle_list = []
        self.listen_state_handle_list = []
        self.timer_handle_list = []
        
        self.player = globals.get_arg(self.args, "player")
        self.presence = globals.get_arg(self.args, "presence")
        self.delay = globals.get_arg(self.args, "delay")
        self.volume = globals.get_arg(self.args, "volume")
        self.master = globals.get_arg(self.args, "master")
        #self.log("{}".format(self.master))
        self.listen_state_handle_list.append(
            self.listen_state(self.presence_change, self.presence)
        )
        self.listen_state_handle_list.append(
            self.listen_state(self.playing_change, self.master)
        )
        self.listen_state_handle_list.append(
            self.listen_state(self.volume_change, self.volume)
        )

    def volume_change(self, entity, attribute, old, new, kwargs):
        self.real_volume = "{}".format(float(self.get_state(self.volume))/100)
        self.log("{}".format(self.real_volume))
        self.log("{}".format(old))
        self.log("{}".format(new))
        if self.get_state(self.presence) == "on":
            if new != old:
                self.log("{}".format(self.real_volume))
                self.call_service("media_player/volume_set", entity_id=self.player, volume_level="{}".format(self.real_volume))
        else: 
            if self.get_state(self.master) != "playing":
                self.call_service("media_player/volume_set", entity_id=self.player, volume_level="0.30")
            else:
                #sleep(self.delay)
                self.call_service("media_player/volume_set", entity_id=self.player, volume_level="0")

    def playing_change(self, entity, attribute, old, new, kwargs):
        self.real_volume = "{}".format(float(self.get_state(self.volume))/100)
        if new == "playing":
            if self.get_state(self.presence) == "on":
            #self.log("{} = {}".format(self.player, self.real_volume))
                self.call_service("media_player/volume_set", entity_id=self.player, volume_level="{}".format(self.real_volume))
            else: 
                self.call_service("media_player/volume_set", entity_id=self.player, volume_level="0")
        else: 
            self.call_service("media_player/volume_set", entity_id=self.player, volume_level="0.30")


    def presence_change(self, entity, attribute, old, new, kwargs):
        self.real_volume = "{}".format(float(self.get_state(self.volume))/100)
        if old != new: 
            if self.get_state(self.master) == "playing":
                if new == "on":
                    self.call_service("media_player/volume_set", entity_id=self.player, volume_level="{}".format(self.real_volume))
                else: 
                    #time.sleep(self.get_state(self.delay))
                    #sleep(self.delay)
                    self.call_service("media_player/volume_set", entity_id=self.player, volume_level="0")

    def terminate(self):
        for listen_state_handle in self.listen_state_handle_list:
            self.cancel_listen_state(listen_state_handle)
            
class MediaPlayer(hass.Hass):
    def initialize(self):
        self.timer_handle = None
        self.listen_event_handle_list = []
        self.listen_state_handle_list = []
        self.timer_handle_list = []

        self.player = globals.get_arg(self.args, "player")
        self.master = globals.get_arg(self.args, "master")
        self.volume = globals.get_arg(self.args, "volume")


    #     self.listen_state_handle_list.append(
    #         self.listen_state(self.presen_change, self.presen_office)
    #     )

    # def presen_change(self, entity, attribute, old, new, volume):
    #     if new != old: 
    #         if new == "on":
    #             self.call_service("media_player/volume_set", entity_id=entity, volume_level=volume)
    #         elif new == "off":
    #             self.call_service("media_player/volume_set", entity_id=entity, volume_level=0)

    def terminate(self):
        for listen_state_handle in self.listen_state_handle_list:
            self.cancel_listen_state(listen_state_handle)