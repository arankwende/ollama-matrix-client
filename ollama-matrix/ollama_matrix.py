import yaml
import datetime
import os
import sys
import logging
import logging.handlers as handlers
import argparse
import asyncio
from ollama import AsyncClient as OllamaAsync
from nio import AsyncClient, MatrixRoom, RoomMessageText


def load_config():
    try:
        config_dir = os.path.dirname(os.path.realpath(__file__))
        config_file = os.path.join(config_dir,'config', 'config.yaml')
        configuration = open(config_file, 'r')
        logging.info(f'Opening the following file: {config_file}')
        config = yaml.safe_load(configuration)
        return config, configuration

    except Exception as exception:
        logging.critical(f"There's an error accessing your config.yml file, the error is the following: {exception}")
        print("There's no config yaml file in the program's folder, please check the logs.")
        sys.exit()


def custom_config(): # placeholder custom config function for -c mode in Cli - Work in progressW
    try:
        MatrixHomeServer= input("Matrix, please enter your Homeserver address:  ")
        MatrixUser= input("Matrix, please enter your complete username:  ")
        MatrixPassword= input("Matrix, please enter your password:  ")
        MatrixRooms= []
        MatrixRoomNumber=int(input("How many rooms will your bot be added to?  "))
        for room in range(0, MatrixRoomNumber):
            room=input("Please write the name of a single room: ")
            MatrixRooms.append(room)
        MatrixDeviceID=input("Please enter the id you will use for this device: ")
        MatrixConfig = {"HOMESERVER":MatrixHomeServer, "USER":MatrixUser, "PASSWORD":MatrixPassword,"ROOMS":MatrixRooms,'ID':MatrixDeviceID}
        OllamaHost=input("Ollama: please enter your Ollama server address and port. If it's local it should be localhost:11434: ")
        OllamaModel=input("Ollama: please enter the name of the model you will be running:  ")
        OllamaPrompt= input("Ollama: please enter the prompt you want to use for your model:  ")
        OllamaConfig={"HOST":OllamaHost, "MODEL":OllamaModel, "PROMPT":OllamaPrompt}
        config = {"MATRIX":MatrixConfig, "OLLAMA":OllamaConfig}
        print(config)
        configuration = yaml.dump(config)
        logging.info(f'Loading a custom config {configuration}')
        return config, configuration
    except Exception as exception:
        logging.critical(f"There's an error loading your custom configuration, the error is the following: {exception}")
        print("There's something missing in the arguments you passed as configuration.")
        sys.exit()   


class OllamaMatrixClient:
    #global args, config, configuration, MatrixConfig, OllamaConfig # We declare global variables for the loaded config


    def __init__(self,args):

        if getattr(args,'c'): #IF the user has set a custom config with the -c cli handle, we load the custom config
            try:
                config, configuration =  custom_config()
            except Exception as exception:
                logging.critical(f'You are missing something in the custom config provided. The exception is {exception} ')
        else:
            try:
                #Otherwise, we try to load yaml configuration files and create variables for the elements in the yaml
                config, configuration = load_config()
            except Exception as exception:
                logging.critical(f'Your YAML is missing something You get the following error: {exception} ')
        try:
            MatrixConfig = config['MATRIX']
            if MatrixConfig is None:
                logging.warning("You have no Matrix configuration set.")  
            else:
                self.MatrixHomeserver=MatrixConfig['HOMESERVER']
                self.MatrixUser=MatrixConfig['USER']
                self.MatrixPassword=MatrixConfig['PASSWORD']
                self.MatrixDeviceID=MatrixConfig['ID']
                self.MatrixRoomsList=MatrixConfig['ROOMS']
                logging.debug(f"This is the Matrix configuration loaded: {str(MatrixConfig)}")
        except Exception as exception:
            logging.critical(f'Your config is missing something in the MATRIX section. You get the following error: {exception} ')
        try:
            OllamaConfig = config['OLLAMA']
            if OllamaConfig is None:
                logging.warning("You have no Ollama configuration set.")  
            else:
                self.OllamaHost=OllamaConfig['HOST']
                self.OllamaModel=OllamaConfig['MODEL']
                self.OllamaPrompt=OllamaConfig['PROMPT']
                logging.debug(f"This is the Ollama configuration loaded: {str(OllamaConfig)}")
        except Exception as exception:
            logging.critical(f'Your config is missing something in the OLLAMA section. You get the following error: {exception} ')
        #Finally we load the AsyncClient for the Matrix connection
        self.client = AsyncClient(self.MatrixHomeserver,self.MatrixUser,self.MatrixDeviceID, ssl=True)
        self.connection_time = datetime.datetime.now()

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        # Main bot functionality
        if isinstance(event, RoomMessageText):
            message_timestamp = event.server_timestamp / 1000
            message_timestamp = datetime.datetime.fromtimestamp(message_timestamp)
            logging.debug(f"Message detected from {message_timestamp}")
            # assign parts of event to variables
            SendMessage = event.body
            MessageSender = event.sender
            room_id = room.room_id
            if message_timestamp > self.connection_time and MessageSender != self.MatrixUser:
                await self.ollama_send(room_id,SendMessage)
            else:
                logging.debug("Message not applicable.")
        
    async def matrix_send(self, MatrixRoomID, MessageBody):
            await self.client.room_send(room_id=MatrixRoomID,message_type="m.room.message",content={"msgtype": "m.text", "body": MessageBody}) 

    async def ollama_send(self, room_id,SendMessage):
        logging.info("Sending chat to Ollama.")
        message = {'role': 'user', 'content': SendMessage}
        #Code snippet to try later to enable streamin
        #async for part in await self.client.chat(model=self.OllamaModel, messages=[message], stream=True):
        #    response= f"({part['message']['content']}, end='', flush=True)"
        #    logging.info(response)
        #    return response
        response = await OllamaAsync(host=self.OllamaHost).chat(model=self.OllamaModel, messages=[message])
        logging.debug(f"The following message was sent to Ollama on{self.OllamaHost} for the model {self.OllamaModel}: {SendMessage}.")
        response_message = response["message"]
        message_content = response_message['content']
        logging.debug(f"The following message was received from Ollama on{self.OllamaHost} for the model {self.OllamaModel}: {message_content}.")
         # Send the response back to the matrix channel
        await self.matrix_send(room_id,message_content)

    async def main(self):

        self.client.add_event_callback(self.message_callback,RoomMessageText)
        try:
            await self.client.login(self.MatrixPassword)
            logging.info(f'Succesfully connected to {self.MatrixHomeserver} with user {self.MatrixUser}.')
            name = await self.client.get_displayname(self.MatrixUser)
        except Exception as exception:
            logging.critical(f"Couldn't connect to {self.MatrixHomeserver} with user {self.MatrixUser}. The exception is {exception}")
        for MatrixRoomID in self.MatrixRoomsList:
            try:
                await self.client.join(MatrixRoomID)
                logging.info(f'Succesfully joined room {MatrixRoomID} with user {self.MatrixUser}.')
            except Exception as exception:
                logging.critical(f"Couldn't join room {MatrixRoomID} with user {self.MatrixUser}. The exception is {exception}")

        await self.client.sync_forever(set_presence="online",timeout=30000) 