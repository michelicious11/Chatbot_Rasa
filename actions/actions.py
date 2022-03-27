# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import os
import time
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionSaveConvo(Action):
    def name(self) -> Text:
        return "action_save_convo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        conversation=tracker.events
        print(conversation)
        # import module  
        current_datetime = time.strftime("%Y%m%d-%H%M%S")
        print("Current date & time : ", current_datetime)
        str_current_datetime = str(current_datetime)
        file_name = "Conversation-"+str_current_datetime+".txt"
        file = open(file_name, 'w')
        if not os.path.isfile(file_name):
            with open( file_name,'w') as file:
                file.write("intent,user_input,entity_name,entity_value,action,bot_reply\n")
        chat_data=''
        for i in conversation:
            if i['event'] == 'user':
                chat_data+='\n'+i['parse_data']['intent']['name']+','+'\n'+i['text']+','+'\n'
                print('user: {}'.format(i['text']))
                if len(i['parse_data']['entities']) > 0:
                    chat_data+=i['parse_data']['entities'][0]['entity']+','+'\n'+i['parse_data']['entities'][0]['value']+','+'\n'
                    print('extra data:', i['parse_data']['entities'][0]['entity'], '=',
                          i['parse_data']['entities'][0]['value'])
                else:
                    chat_data+='\n'+",\n,"+'\n'
            elif i['event'] == 'bot':
                print('Bot: {}'.format(i['text']))
                try:
                    chat_data+='\n'+i['metadata']['utter_action']+','+'\n'+i['text']+'\n'
                except KeyError:
                    pass
        else:
            with open(file_name,'a') as file:
                file.write(chat_data)

        return []
