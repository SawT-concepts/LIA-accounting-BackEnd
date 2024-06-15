# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PayrollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'payroll_updates'
        print("connected")
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.send(
            
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print("disconnected")
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    # Receive message from room group
    async def payroll_update(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
