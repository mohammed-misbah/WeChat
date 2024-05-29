from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json

class ChatConsumer(AsyncWebsocketConsumer):
# Connect a Websocket
    print("Entered Consumers class")

    async def connect(self):
        print("Connected websocket")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

# Disconnect  from websocket-----------------------------

    async def disconnect(self, close_code):
        # Leave a room group
        print(f"Disconnected with close code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

# Receive message from WebSocket

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print(message, "<<<Receiveeeeeeeee>>>", text_data_json)

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                'type': 'chat_message',
                'message' : message
            } 
        )


    # Receive message from room group

    async def chat_message(self, event):
        message = event['message']

        # Send message to Websocket
        await self.send(text_data=json.dumps({
            'message': message
        }))








    # def connect(self):
    #     self.room_name = self.scope['url_route']['kwargs']['room_name']
    #     self.room_group_name = 'chat_%s' % self.room_name

    #     # Join to group
    #     async_to_sync(self.channel_layer.group_add)(
    #         self.room_group_name,
    #         self.channel_name
    #     )
    #     self.accept()




    # async def receive(self, text_data):
    #     try:
    #         text_data_json = json.loads(text_data)
    #         message = text_data_json['message']
    #         async_to_sync(self.channel_layer.group_send)(
    #             self.room_group_name,
    #             {
    #                 'type' : 'chat_message',
    #                 'message': message  
    #             }
    #         )
    #     except json.JSONDecodeError as e:
    #         print(f"Error decoding JSON: {e}")
    #     except KeyError as e:
    #         print(f"Missing expected key in JSON data: {e}")