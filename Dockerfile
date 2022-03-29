FROM ubuntu:20.04
ENTRYPOINT []
RUN apt-get update && apt-get install -y python3 python3-pip && python3 -m pip install --no-cache --upgrade pip && pip3 install --no-cache rasa==3.0.6
RUN chmod +x /Chatbot_Rasa/start_services.sh
CMD /Chatbot_Rasa/start_services.sh