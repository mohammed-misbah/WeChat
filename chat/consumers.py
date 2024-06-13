from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Message
import json
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    async def fetch_messages(self, data):
        """
        Asynchronously fetches the last 10 messages from the database and sends them over a WebSocket.

        This function retrieves the last 10 messages from the message database using an asynchronous call,
        converts these messages to JSON format using the `messages_to_json` method, and constructs a
        command package that includes the messages. The package is then sent over the WebSocket connection.

        Args:
            data (dict): A dictionary that can include additional data used in fetching messages.
                        Currently, it does not influence the fetching within this function.

        Returns:
            None: This function does not return a value but sends messages via WebSocket.
        """
        messages = await sync_to_async(list)(Message.last_10_messages())
        json_messages = await self.messages_to_json(messages)
        content = {
            'command': 'messages',
            'messages': json_messages
        }
        await self.send_chat_message(content)


    async def new_messages(self, data):
        """
        Handles the creation of a new message and sends it over a WebSocket.

        This function retrieves the author from the provided `data` dictionary, fetches
        the corresponding user object from the database asynchronously, and creates a
        new message with the content also specified in `data`. The newly created message
        is then converted to JSON format and sent over the WebSocket channel as part
        of a command package.

        Args:
            data (dict): A dictionary containing 'from' and 'message' keys representing 
                        the author's username and the message content, respectively.

        Returns:
            None: This function does not return a value but sends a message via WebSocket.
        """
        author = data['from']
        # author_user = User.objects.filter(username = author)[0]
        author_user = await sync_to_async(User.objects.get)(username=author)
        message = await sync_to_async(Message.objects.create)(
            author=author_user,
            content=data['message']
        )
        json_message = await self.message_to_json(message)
        content = {
            'command': 'new_messages',
            'message': json_message
        }
        await self.send_chat_message(content)


    async def messages_to_json(self, messages):
        """
        Asynchronously converts a list of message objects into JSON format.

        This function iterates over each message in the provided list, `messages`,
        and converts each message to JSON format using the `message_to_json` method.
        The conversion is performed asynchronously for each message.

        Args:
            messages (list): A list of message objects to be converted.

        Returns:
            list: A list of messages in JSON format, obtained by asynchronously 
                converting each message in the input list.
        """
        return [
            await self.message_to_json(message) 
            for message in messages
        ]
    

    async def message_to_json(self, message):
        """
        Converts a message object to a JSON format dictionary.

        This function asynchronously retrieves the username of the message author and constructs a
        dictionary with the author's username, message content, and timestamp. The timestamp is
        converted to a string format for easier handling.

        Args:
            message (Message): The message object to be converted.

        Returns:
            dict: A dictionary containing the 'author', 'content', and 'timestamp' of the message.
        """
        author_username = await sync_to_async(lambda: message.author.username)()
        return {
            'author': author_username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }
    
    ######################
    """
    Dictionary to map command strings to corresponding functions.

    This dictionary is used to define which function should be called based on command names received 
    from client-side interactions. Each key in the dictionary is a command name as a string, and the 
    associated value is the function that should be executed when that command is received.

    Commands:
        'fetch_messages' : Function to fetch and send the last set of messages from the chat history.
        'new_messages' : Function to create a new message and broadcast it to the chat.

    This allows for dynamic function calling based on client requests, facilitating a modular and 
    extendable command handling system for WebSocket communication.
    """
    commands = {
        'fetch_messages' : fetch_messages,
        'new_messages' : new_messages
    }

    #######################

    async def connect(self):
        """
        Establishes a WebSocket connection and adds the current channel to a chat group.

        This function is called when a WebSocket connection is initiated. It prints a connection message,
        retrieves the room name from the URL route, forms a group name for the chat, and then adds this
        WebSocket channel to the corresponding group in the channel layer. Finally, it accepts the WebSocket
        connection to start receiving messages.

        Args:
            None

        Returns:
            None: This function does not return a value but establishes a WebSocket connection and subscribes
                the connection to a group for receiving messages.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    

    async def disconnect(self, close_code):
        """
        Handles the disconnection of a WebSocket connection.

        This function is called when a WebSocket is disconnected. It prints the disconnection code to
        the console for debugging purposes. It also removes the WebSocket channel from the associated
        chat group to stop receiving further messages.

        Args:
            close_code (int): The code indicating why the WebSocket was closed, useful for understanding
                            the reason for disconnection.

        Returns:
            None: This function does not return a value but ensures the channel is removed from the group.
        """
        print(f"Disconnected with close code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

# Receive message from WebSocket

    async def receive(self, text_data):
        """
        Asynchronously processes incoming WebSocket text data based on a command.

        This function looks at the received `text_data` and finds out what task it is supposed to do, 
        called a 'command'. It then checks if this command is one it knows how to handle, 
        which it keeps in a list called `self.commands`. If it finds the command in the list, 
        it does what the command says using the information provided.

        Args:
            text_data (str): A JSON string containing at least a 'command' key. This string represents 
                            the data received over the WebSocket.

        Returns:
            None: This function does not return a value but invokes another function based on the command.
        """
        data = json.loads(text_data)
        command = data.get('command')
        if command in self.commands:
            await self.commands[command](self, data)


    async def send_chat_message(self, message):
        """
        Asynchronously sends a chat message to the group associated with the WebSocket.

        This function shows the message it is about to send, and then sends it to everyone in the
        group members associated with `self.room_group_name`. It labels the message in a way that 
        lets the receivers know it's a chat_message.

        Args:
            message (dict): The message content to send. It should be a dictionary containing the 
                            actual message and potentially other metadata.

        Returns:
            None: This function does not return a value but performs an asynchronous operation to
                send a message to a WebSocket group.
        """
        print('Sending message:>>>', message)
        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                'type': 'chat_message',
                'message': message
            } 
        )

    # Receive message from room group for every event occur(entering a new message)

    # Send message to Websocket
    async def chat_message(self, event):
        """
        Handles the reception of a chat message event and sends it to the WebSocket client.

        This function is triggered when a chat message event is received. It extracts the message 
        from the event, prints a confirmation to the console, and then sends this message as JSON 
        to the connected WebSocket client.

        Args:
            event (dict): A dictionary containing the 'message' key with the chat message data.

        Returns:
            None: This function does not return a value but sends the message to the client over WebSocket.
        """
        message = event['message']
        print("Messssssssssssages are: >>>", message)
        await self.send(text_data=json.dumps(message))


