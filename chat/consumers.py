from channels.generic.websocket import WebsocketConsumer
import json

class ChatConsumer(WebsocketConsumer):
# Connect a Websocket
    print("Entered Consumers class")
    def connect(self):
        print("Connected websocket")
        self.accept()
# Disconnect  from websocket-----------------------------
    def disconnect(self, close_code):
        pass

# Receive message from WebSocket
    def receive(self, text_data):
        print("Entered received function")
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({
            "message": message
            })
        )