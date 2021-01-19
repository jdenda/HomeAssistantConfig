import appdaemon.plugins.hass.hassapi as hass
import globals
import datetime
import math

class baClock(hass.Hass):
    def initialize(self):
        self.timer_handle_list = []
        self.listen_event_handle_list = []
        self.listen_state_handle_list = []
        self.alarm_time = globals.get_arg(self.args, "alarm_time")
        self.num_naturalwakeup = globals.get_arg(self.args, "num_naturalwakeup")
        self.bool_wakemeup = globals.get_arg(self.args, "bool_wakemeup")
        self.light_wakeup = globals.get_arg(self.args, "light_wakeup")
        self.motion_trigger = globals.get_arg(self.args, "motion_trigger")
        self.boool_nightmode = globals.get_arg(self.args, "boool_nightmode")
        self.fade_in_time_multiplicator = globals.get_arg(self.args, "fade_in_time_multiplicator")
        try: 
            self.bool_alarmweekday = globals.get_arg(self.args, "bool_alarmweekday")
        except: 
            self.log("coudnt set bool_alarmweekday")
            self.bool_alarmweekday = None
        try: 
            self.bin_isweekday = globals.get_arg(self.args, "bin_isweekday")
        except: 
            self.log("coudnt set bin_isweekday")
            self.bin_isweekday = None
        try: 
            self.bool_radiowakeup = globals.get_arg(self.args, "bool_radiowakeup")
        except: 
            self.log("coudnt set bool_radiowakeup")
            self.bool_radiowakeup = None
        try: 
            self.switch_adaptive_light = globals.get_arg(self.args, "switch_adaptive_light")
        except: 
            self.log("coudnt set switch_adaptive_light")
            self.switch_adaptive_light = None
        try: 
            self.entity_kill_clock = globals.get_arg(self.args, "entity_kill_clock")
        except: 
            self.log("coudnt set entity_kill_clock")
            self.entity_kill_clock = None
        try: 
            self.num_volume = globals.get_arg(self.args, "num_volume")
        except: 
            self.log("coudnt set num_volume")
            self.num_volume = None
        try: 
            self.script_post = globals.get_arg(self.args, "script_post")
        except: 
            self.log("coudnt set script_post")
            self.script_post = None

        self.alarm_timer = None

        self.cached_alarm_time = self.get_state(self.alarm_time)
        self.cached_fade_in_time = self.get_state(self.num_naturalwakeup)
        self.add_timer()

        self.listen_state_handle_list.append(
            self.listen_state(self.alarm_change, self.alarm_time)
        )
        self.listen_state_handle_list.append(
            self.listen_state(self.naturalwakeup_change, self.num_naturalwakeup)
        )

    def alarm_change(self, entity, attributes, old, new, kwargs):
        if new is not None and new != old and new != self.cached_alarm_time:
            if self.alarm_timer is not None:
                if self.alarm_timer in self.timer_handle_list:
                    self.timer_handle_list.remove(self.alarm_timer)
                self.cancel_timer(self.alarm_timer)
            self.log("Alarm time change: {}".format(new))
            self.cached_alarm_time = new
            self.add_timer()

    def naturalwakeup_change(self, entity, attributes, old, new, kwargs):
        if new is not None and new != old and new != self.cached_fade_in_time:
            if self.alarm_timer is not None:
                if self.alarm_timer in self.timer_handle_list:
                    self.timer_handle_list.remove(self.alarm_timer)
                self.cancel_timer(self.alarm_timer)
            self.log("Fade-In time change: {}".format(new))
            self.cached_fade_in_time = new
            self.add_timer()

    def add_timer(self):
        self.log("cached_alarm_time: {}".format(self.cached_alarm_time))
        self.log("cached_fade_in_time: {}".format(self.cached_fade_in_time))
        offset = self.cached_fade_in_time.split(".", 1)[0]

        if self.cached_alarm_time is not None and self.cached_alarm_time != "":
            run_datetime = datetime.datetime.strptime(
                self.cached_alarm_time, "%Y-%m-%d %H:%M:%S"
            )
            event_time = run_datetime - datetime.timedelta(minutes=int(offset))
            try:
                self.alarm_timer = self.run_at(self.trigger_alarm, event_time)
                self.timer_handle_list.append(self.alarm_timer)
                self.log("Alarm will trigger at {}".format(event_time))
            except ValueError:
                self.log("New trigger time would be in the past: {}".format(event_time))

    def trigger_alarm(self, kwargs):
        self.log("Alarm was triggered")
        self.call_service("notify/janneck_telegram", message="Wecker ausgelöst")
        if self.get_state(self.wakemeup) == "on":
            self.log("Trigger")