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


class CashbookConsumer (AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'cashbook_updates'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from room group
    async def receive (self, text_data):
        pass


    async def cashbook_update (self, event):
        message = event['message']
        data = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'data': data
        }))



    class GlobalUpdateConsumer (AsyncWebsocketConsumer):

        DATA_CATEGORY = {
            "PAYROLL": "payroll_updates",
            "CASHBOOK": "cashbook_updates",
            "NOTIFICATION": "notification_updates",
            "TRANSACTION": "transaction_updates",
            "STUDENT": "student_updates",
            "TEACHER": "teacher_updates",
            "ADMIN": "admin_updates",
        }

        async def connect(self):
            self.group_name = 'global_updates'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def recieve (self, text_data):
        pass

    async def global_update (self, event):
        message = event['message']
        data = event['data']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'data': data
        }))
