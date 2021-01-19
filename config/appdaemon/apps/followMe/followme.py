import appdaemon.plugins.hass.hassapi as hass
import globals

class followMe(hass.Hass):
    def initialize(self):
        self.lead = globals.get_arg(self.args, "lead")
        self.follow = globals.get_arg(self.args, "follow")
        self.attributes = globals.get_arg(self.args, "attributes")
        self.listen_state_handle_list = []
        self.listen_state_handle_list.append(
            self.listen_state(self.lead_change, self.lead)
        )

    def lead_change(self, entity, attribute, old, new, kwargs):
        if old != new: 
            self.log("Set Attributes: "+str(self.attributes))
            if self.attributes == True: 
                self.log("Lead "+str(self.lead)+" changed to "+str(self.get_state(self.lead)))
                lead_service = self.get_service(self.lead)
                self.log("Service Lead: "+str(lead_service))
                follow_service = self.get_services(self.follow)
                self.log("Service Follow: "+str(follow_service))
            else: 
                self.log("Setting Entities")
                if isinstance(self.follow, list):
                    for x in self.follow: 
                        self.log("homeassistant.turn_"+str(new)+" entity: "+str(x))
                        self.call_service(
                            "light/turn_"+str(new), entity=str(x)
                        )
                else: 
                    self.log("homeassistant.turn_"+str(new)+" entity: "+str(x))
                    self.call_service(
                        "light/turn_"+str(new), entity=self.follow
                    )

                    self.call_service(
                        "light/turn_on", entity_id=light
                    )

    def get_services(self, entity):
        if isinstance(entity, list): 
            helper = []
            for x in entity:
                helper.append(self.get_service(x))
            return helper
        else:
            return get_service(entity)

    def get_service(self, entity):
        entity = str(entity)
        entity = entity.split('.')
        entity = entity[0]
        return entity

