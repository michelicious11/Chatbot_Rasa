# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import os
import time
from pathlib import Path
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from utils.utils import get_html_data, send_email

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


class ValidateContactUsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_contact_us_form"

    def validate_name(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        if value is not None:
            return {"name": value}
        else:
            return {"requested_slot": "name"}

    def validate_email(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        if value is not None:
            return {"email": value}
        else:
            return {"requested_slot": "email"}


    def validate_confirm_details(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[str, str]:
        intent_name = tracker.get_intent_of_latest_message()
        if value is not None:
            if intent_name in ["affirm", "deny"]:
                return {"confirm_details": intent_name}
        else:
            return {"requested_slot": "confirm_details"}


class ActionSubmitContactForm(Action):
    def name(self) -> Text:
        return "action_submit_contact_us_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        confirm_details = tracker.get_slot("confirm_details")
        name = tracker.get_slot("name")
        email = tracker.get_slot("email")
        message = tracker.get_slot("message")
        if confirm_details == "affirm":
            this_path = Path(os.path.realpath(__file__))
            user_content = get_html_data(f"{this_path.parent}/utils/user_mail.html")
            send_email("Merci de nous avoir contacté", email, user_content)
            admin_content = get_html_data(f"{this_path.parent}/utils/admin_mail.html")
            admin_content.format(
                name=name,
                email=email,
                message=message,
            )
            is_mail_sent = send_email(f"{email.split('@')[0]} nous a contacté!", "chatbotuqotest@gmail.com", admin_content)
            if is_mail_sent:
                dispatcher.utter_message(template="utter_mail_success")
                dispatcher.utter_message(template="utter_feedback")
            else:
                dispatcher.utter_message("Désolé, je n'ai pas pu envoyer de courriel. Veuillez réessayer plus tard.")
                dispatcher.utter_message(template="utter_feedback")
        else:
            dispatcher.utter_message(template="utter_mail_canceled")
            dispatcher.utter_message(template="utter_feedback")
        return []