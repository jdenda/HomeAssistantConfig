import appdaemon.plugins.hass.hassapi as hass
import globals

class TagScanner(hass.Hass):
    def initialize(self):
        self.listen_event_handle_list = []

        self.tag = globals.get_arg(self.args, "tag")
        try: 
            self.script = globals.get_arg(self.args, "script")
            self.log("script set to "+self.script)
        except: 
            self.script = None
            self.log("No script set!")
        try: 
            self.entity = globals.get_arg(self.args, "entity")
            self.log("entity set to "+self.entity)
        except: 
            self.entity = None
            self.log("No entity set!")
        try: 
            self.action = globals.get_arg(self.args, "action")
            self.log("action set to "+self.action)
        except: 
            self.action = None
            self.log("No action set!")


        self.listen_event_handle_list.append(
            self.listen_event(self.scanned, "tag_scanned", tag_id = str(self.tag))
        )

    def scanned(self, entity, attribute, old):
        self.log("Tag "+str(self.tag)+" scanned!")
        if (self.entity != None):
            s = self.entity.split(".")
            self.log("Service: "+s[0])
            if self.action == None: 
                self.call_service(
                    ""+s[0]+"/toggle", entity_id=self.entity
                )
            else: 
                self.call_service(
                    ""+s[0]+"/turn_"+str(self.action)+"", entity_id=self.entity
                )
        if (self.script != None):
            self.log("Script "+str(self.script))
            self.call_service(
                "script/turn_on", entity_id=self.script
            )