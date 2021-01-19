import appdaemon.plugins.hass.hassapi as hass
import globals
import requests

class Cloudflare(hass.Hass):
    def initialize(self):
        self.api_token = globals.get_arg(self.args, "api_token")
        self.zone = globals.get_arg(self.args, "zone")
        self.email = globals.get_arg(self.args, "email")
        self.global_token = globals.get_arg(self.args, "global_token")
        self.timer = globals.get_arg(self.args, "timer")
        response = requests.get('https://api.cloudflare.com/client/v4/user/tokens/verify', headers={"Authorization": "Bearer "+self.api_token, "Content-Type": "application/json"})
        self.log("Api Token verified: "+ str(response))
        response = requests.get('https://api.cloudflare.com/client/v4/zones/'+self.zone, headers={"Authorization": "Bearer "+self.api_token, "Content-Type": "application/json"})
        self.log("Zone verified: "+ str(response))
        response = requests.get('https://api.cloudflare.com/client/v4/user', headers={"X-Auth-Email": self.email, "X-Auth-Key": self.global_token, "Content-Type": "application/json"})
        self.log("Global Token verified: "+ str(response))
        response = requests.get('https://api.cloudflare.com/client/v4/zones/'+self.zone+'/dns_records', headers={"X-Auth-Email": self.email, "X-Auth-Key": self.global_token, "Content-Type": "application/json"})
        self.log("DNS records verified: "+ str(response))
        self.run_every(self.update, "now", self.timer * 60)

    def update(self, kwargs):
        response = requests.get('https://api.cloudflare.com/client/v4/zones/'+self.zone+'/dns_records', headers={"X-Auth-Email": self.email, "X-Auth-Key": self.global_token, "Content-Type": "application/json"})
        records = response.json()
        records = records["result"]
        for record in records:
            try:
                self.log(record["name"]+" "+record["type"]+" "+record["content"]+" "+str(record["proxied"])+" ")
                sensor = "sensor.cloudflare_domain_"+((str(record["name"])).replace(".","_")).replace("*", "star")
                self.set_state(sensor, state=record["type"], attributes={"friendly_name": (str(record["name"])).replace("*", "star"), "record": record["content"], "proxied": str(record["proxied"])})
            except: 
                self.log("Error adding entity")
