import json
from chat import models as chat_models
from channels.db import database_sync_to_async
from base import models as base_models
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def create_message(self, sender, content, group_id):
        group = base_models.Groups.objects.get(id=group_id)
        chat_models.Messages.objects.create(sender = sender, group = group, content = content)


    async def connect(self):
        self.roomName = self.scope["url_route"]["kwargs"]["room_name"]
        self.roomGroupName = f"{self.roomName}"
        await self.channel_layer.group_add(
            self.roomGroupName ,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self , close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName , 
            self.channel_name 
        )
        

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        room_name1 = text_data_json["chat_room_id"]

        chat = chat_models.Messages(
            sender = username,
            room_name = room_name1,
            content = message
        )

        await database_sync_to_async(chat.save)()
        
        await self.channel_layer.group_send(
            self.roomGroupName,{
                "type" : "sendMessage" ,
                "message" : message , 
                "username" : username ,
                "chat_room_id": room_name1,
            })
        
    async def sendMessage(self , event) : 
        message = event["message"]
        username = event["username"]
        room_name1 = event["chat_room_id"]
        #new_msg = await self.create_message(username, message, group_id)
        await self.send(text_data = json.dumps({"message":message ,"username":username, "chat_room_id":room_name1}))
      
