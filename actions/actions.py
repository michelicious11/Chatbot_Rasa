# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import os
import time
import smtplib
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        SendEmail(
            tracker.get_slot("email"),
            tracker.get_slot("subject"),
            tracker.get_slot("message")
        )
        dispatcher.utter_message("Merci d'avoir fourni les détails. Nous vous avons envoyé un courriel de confirmation à {}".format(tracker.get_slot("email")))
        return []

def SendEmail(toaddr,subject,message):
    fromaddr = "chatbotuqotest@gmail.com"
    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = subject

    # string to store the body of the mail
    body = message

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    # filename = "/home/ashish/Downloads/webinar_rasa2_0.png"
    # attachment = open(filename, "rb")
    #
    # # instance of MIMEBase and named as p
    # p = MIMEBase('application', 'octet-stream')
    #
    # # To change the payload into encoded form
    # p.set_payload((attachment).read())
    #
    # # encode into base64
    # encoders.encode_base64(p)
    #
    # p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    #
    # # attach the instance 'p' to instance 'msg'
    # msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()


    # Authentication
    try:
        s.login(fromaddr, "l3jFaFQcjI6BotEr")

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, toaddr, text)
    except:
        print("Une erreur s'est produite lors de l'envoi du courriel. Veuillez réessayer ultérieurement.")
    finally:
        # terminating the session
        s.quit()
