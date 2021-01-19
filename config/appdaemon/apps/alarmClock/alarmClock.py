import appdaemon.plugins.hass.hassapi as hass
import globals
import datetime
import math


#
# Alarm Clock App
#
#
# Args:
#  alarm_time: entity which holds the alarm time. example: sensor.alarm_time
#  wakemeup: entity which enables the alarm. example: input_boolean.wakemeup
#  naturalwakeup: entity which enables the natural wake up fade in. example: input_number.alarm_natural_wakeup_fade_in
#  alarmweekday: entity which enables alarm only on weekdays. example: input_boolean.alarmweekday
#  radiowakeup: entity which enables radio wake up. example: input_boolean.radiowakeup
#  TODO radioplayer: entity which holds the information which radio player to select. example: input_select.wakeup_radioplayer
#  wakeup_light: light to fade in. example: light.bedroom_yeelight
#  isweekday: entity which holds the information whether today is a week day. example: binary_sensor.workday_today
#  notify_name: Who to notify. example: group_notifications
#  message: localized message to use in notification. e.g. "You left open {} Dummy."
#
# Release Notes
#
# Version 1.3.1:
#   Use consistent message variable
#
# Version 1.3:
#   Use new formatted alarm_time
#
# Version 1.2:
#   use Notify App
#
# Version 1.1:
#   message now directly in own yaml instead of message module
#
# Version 1.0:
#   Initial Version


class AlarmClock(hass.Hass):
    def initialize(self):

        self.timer_handle_list = []
        self.listen_event_handle_list = []
        self.listen_state_handle_list = []

        self.alarm_time = globals.get_arg(self.args, "alarm_time")
        self.circadian_1 = globals.get_arg(self.args, "circadian_switch")
        # self.circadian_2 = globals.get_arg(self.args, "circadian_switch_2")
        self.wakemeup = globals.get_arg(self.args, "wakemeup")
        self.off = globals.get_arg(self.args, "entity_off")
        self.naturalwakeup = globals.get_arg(self.args, "naturalwakeup")
        self.alarmweekday = globals.get_arg(self.args, "alarmweekday")
        self.radiowakeup = globals.get_arg(self.args, "radiowakeup")
        self.isweekday = globals.get_arg(self.args, "isweekday")
        self.motion = globals.get_arg(self.args, "deactivate_motionTrigger")
        # self.motion2 = globals.get_arg(self.args, "deactivate_motionTrigger_2")
        self.wakeup_light = globals.get_arg(self.args, "wakeup_light")
        self.volume = globals.get_arg(self.args, "volume")
        self.nacht = globals.get_arg(self.args, "nacht")
        self.player = self.get_app("mediaPlayerStartPlayback")
        self.kaffee = globals.get_arg(self.args, "kaffescript")
        self.fade_in_time_multiplicator = globals.get_arg(
            self.args, "fade_in_time_multiplicator"
        )

        self.brightness = 100
        self.rgb_color = [255, 120, 0]
        self.alarm_timer = None

        self.cached_alarm_time = self.get_state(self.alarm_time)
        self.cached_fade_in_time = self.get_state(self.naturalwakeup)
        self.add_timer()

        self.listen_state_handle_list.append(
            self.listen_state(self.alarm_change, self.alarm_time)
        )
        self.listen_state_handle_list.append(
            self.listen_state(self.naturalwakeup_change, self.naturalwakeup)
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
            if self.get_state(self.alarmweekday) == "off" or (
                self.get_state(self.alarmweekday) == "on"
                and self.get_state(self.isweekday) == "on"
            ):
                if float(self.cached_fade_in_time) > 0:
                    self.log(
                        "Turning on {}".format(self.friendly_name(self.wakeup_light))
                    )
                    self.call_service(
                        "light/turn_on", entity_id=self.wakeup_light, brightness_pct=1
                    )
                    transition = int(
                        float(self.cached_fade_in_time)
                        * int(self.fade_in_time_multiplicator)
                    )
                    self.log(
                        "Transitioning light in over {} seconds".format(transition)
                    )
                    self.call_service(
                        "switch/turn_off", entity_id=self.circadian_1
                    )
                    # self.call_service(
                    #     "switch/turn_off", entity_id=self.circadian_2
                    # )
                    self.call_service(
                        "input_boolean/turn_off", entity_id=self.motion
                    )
                    # self.call_service(
                    #     "automation/turn_off", entity_id=self.motion2
                    # )
                    try:
                        self.player.play(
                            "Guten Morgen", "Schlafzimmer", "janneck_telegram"
                        )
                    except TimeoutError:
                        self.log("timeouterror starting playback, can be ignored") 
                    self.call_service(
                        "input_number/set_value", entity_id=self.volume, value=15
                    )
                    self.timer_handle_list.append(
                        self.run_in(
                            self.run_fade_in, 1, transition=transition, brightness_pct=1
                        )
                    )
                #  self.timer_handle_list.append(
                #      self.run_in(self.run_alarm, float(self.cached_fade_in_time))
                #  )

    # def button_clicked(self, event_name, data, kwargs):
    #     """Extra callback method to trigger the wakeup light on demand by pressing a Xiaomi Button"""
    #     if data["entity_id"] == self.button:
    #         if data["click_type"] == "single":
    #             if float(self.cached_fade_in_time) > 0:
    #                 self.log(
    #                     "Turning on {}".format(self.friendly_name(self.wakeup_light))
    #                 )
    #                 self.call_service(
    #                     "light/turn_on", entity_id=self.wakeup_light, brightness_pct=1
    #                 )
    #                 transition = int(
    #                     float(self.cached_fade_in_time)
    #                     * int(self.fade_in_time_multiplicator)
    #                 )
    #                 self.log(
    #                     "Transitioning light in over {} seconds".format(transition)
    #                 )
    #                 self.timer_handle_list.append(
    #                     self.run_in(
    #                         self.run_fade_in, 1, transition=transition, brightness_pct=1
    #                     )
    #                 )

    def run_fade_in(self, kwargs):
        """
        Callback / recursion style because the transition feature does not seem to work well with Yeelight for
        transition values greater than 10s.
        :param kwargs:
        :return:
        """
        wait_factor = 1
        transition = kwargs["transition"]
        brightness_pct = kwargs["brightness_pct"]
        pct_increase = 1 / transition
        self.log("pct_increase: {}".format(pct_increase), level="DEBUG")
        if pct_increase < 0.01:
            wait_factor = math.ceil(0.01 / pct_increase)
            pct_increase = 0.01
            self.log(
                "pct_increase smaller than 1% next run_in in {} seconds".format(
                    wait_factor
                ),
                level="DEBUG",
            )
        brightness_pct_old = brightness_pct
        self.log("brightness_pct_old: {}".format(brightness_pct_old), level="DEBUG")
        brightness_pct_new = int((brightness_pct_old + pct_increase * 100))
        self.log("brightness_pct_new: {}".format(brightness_pct_new), level="DEBUG")
        if brightness_pct_new < 100:
            self.call_service(
                "light/turn_on",
                entity_id=self.wakeup_light,
                rgb_color=self.rgb_color,
                brightness_pct=brightness_pct_new,
            )
            if brightness_pct_new < 50:
                self.call_service(
                    "input_number/set_value", entity_id=self.volume, value=brightness_pct_new
                )
            self.timer_handle_list.append(
                self.run_in(
                    self.run_fade_in,
                    wait_factor,
                    transition=transition,
                    brightness_pct=brightness_pct_new,
                )
            )
        else: 
            self.call_service(
                "switch/turn_on", entity_id=self.circadian_1
            )
            # self.call_service(
            #     "switch/turn_on", entity_id=self.circadian_2
            # )
            self.call_service(
                "input_boolean/turn_on", entity_id=self.motion
            )
            # self.call_service(
            #     "automation/turn_on", entity_id=self.motion2
            # )
            self.call_service(
                "input_boolean/turn_off", entity_id=self.nacht
            )
            self.call_service(
                "script/turn_on", entity_id= self.kaffee
            )
            self.turn_off

    # def run_alarm(self, kwargs):
    #     self.notifier.notify(self.notify_name, self.message)
    #     # TODO radio

    def turn_light_off(self):
        if self.get_state(self.off) == "on":
            self.call_service(
                "light/turn_off", entity_id=self.wakeup_light
            )
        else:
            time.sleep(5)
            self.turn_light_off

    def terminate(self):
        self.call_service(
            "switch/turn_on", entity_id=self.circadian_1
        )
        # self.call_service(
        #     "switch/turn_on", entity_id=self.circadian_2
        # )
        self.call_service(
            "input_boolean/turn_on", entity_id=self.motion
        )
        # self.call_service(
        #     "automation/turn_on", entity_id=self.motion2
        # )
        self.call_service(
            "input_boolean/turn_off", entity_id=self.nacht
        )
        for timer_handle in self.timer_handle_list:
            self.cancel_timer(timer_handle)

        for listen_event_handle in self.listen_event_handle_list:
            self.cancel_listen_event(listen_event_handle)

        for listen_state_handle in self.listen_state_handle_list:
            self.cancel_listen_state(listen_state_handle)