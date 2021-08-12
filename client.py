import logging
import base64
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
ENDC = '\033[0m'

class Client(slixmpp.ClientXMPP):
    
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)
        self.add_event_handler('register', self.register)

        self.add_event_handler("message", self.get_message)
        self.add_event_handler("chatstate_composing", self.receive_notification)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        def delete_account():
            self.register_plugin('xep_0030') # Service Discovery
            self.register_plugin('xep_0066')
            self.register_plugin('xep_0199') # xmpp Ping
            self.register_plugin('xep_0004')
            self.register_plugin('xep_0077')

            response = self.Iq()
            response['type'] = 'set'
            response['from'] = self.boundjid.user
            response['register']['remove'] = True
            response.send()

            self.disconnect()
        

        
        show = True
        menu = '''
        1. Log Out
        2. Delte Account
        3. Show contacts
        4. Contact Details
        5. Add Contact
        6. Send Private Message
        7. Join Group
        8. Send Group Message
        9. Define Presence
        10. Chat Answers
        '''
        while(show):
            print('-'*50)
            print(menu)
            print('-'*50)

            choose = input('Choose an option: ')

            if choose == '1':
                print('Log Out')
                self.disconnect()
                show = False
            elif choose == '2':
                print('Delete Account')
                delete_account()
                show = False
            elif choose == '3':
                print(GREEN+'Show Contacts'+ENDC)
                self.show_contacts()
            elif choose == '4':
                print(GREEN+'Contact Details'+ENDC)
                self.show_contact_details()
            elif choose == '5':
                print('Add Contact')
                self.add_contact()
            elif choose == '6':
                print('Send Private Message')
                self.private_message()
            elif choose == '7':
                print('Join Group')
                self.join_group()
            elif choose == '8':
                print('Send Group Message')
                self.send_group_message()
            elif choose == '9':
                print('Define Presence')
                self.change_presence()
            elif choose == '10':
                print('Chat Answers')
            else:
                print('Invalid Option')

            await self.get_roster()

    def invite_group(self):
        room = input("Write the group name: ")
        username = input("Who do you wanna invite: ")
        self.plugin['xep_0045'].invite(room=room+'@conference.alumchat.xyz', jid=username)

    def join_group(self):
        #self.plugin['xep_0045'].join_muc("Prueba@conference.redes2020.xyz", "pruebaaa")
        room = input("Write the group name: ")
        nickname = input("write your nickname: ")
        self.plugin['xep_0045'].join_muc(room+"@conference.alumchat.xyz", nickname)
        #self.plugin['xep_0045'].set_affiliation(room="hola@conference.alumchat.xyz",  affiliation='member',jid=self.boundjid.full,)
    def send_group_message(self):
        
        #self.plugin['xep_0045'].join_muc('grupo', 'prueba')
        #group_name = input('Escriba el nombre del grupo: ')
        #group_name = 'hola@conference.alumchat.xyz'
        room = input("Write the group name: ")
        message = input('Write your message: ')
        #message = 'hola'
        self.send_message(mto=room+"@conference.alumchat.xyz", mbody=message, mtype='groupchat')
    
    def private_message(self):
        #recipient = 'andy@alumchat.xyz'
        #message = 'Hola'

        recipient = input('Who are you sending the message to: ')
        message = input('Write your message: ')
        self.send_notification(recipient, "composing")
        try:
            self.send_notification(recipient, "paused")
            self.send_message(mto=recipient, mbody=message, mtype='chat')
            print('Se envio el mensaje')
            logging.info('Message sent')

        except IqError:
            logging.error('Error in message')
        except IqTimeout:
            logging.error('No server response')

    def show_contact_details(self):
        self.get_roster()

        username = input('Write the username: ')
        #username = 'andy@alumchat.xyz'

        contact = self.client_roster[username]
        print('-'*40)
        if contact['name']:
            print(BLUE+'Nombre: '+CYAN, contact['name'],ENDC+'\n')
        print(BLUE+'Username: '+CYAN,username,ENDC+'\n')
        connections = self.client_roster.presence(username)

        if connections=={}:
            print(BLUE+'Estado: Offline'+ENDC)
        else:
            for client, status in connections.items():
                print(BLUE+'Estado: '+CYAN,status['status'],ENDC)

        print('-'*40)

    def show_contacts(self):
        groups = self.client_roster.groups()
        
        for group in groups:
            print('-'*25)
            for username in groups[group]:
                name = self.client_roster[username]['name']
                if name:
                    print(BLUE+'Nombre: ',name,ENDC)
                    print(BLUE+'Usuario: '+CYAN,username,ENDC)
                else:
                    print(BLUE+'Usuario: '+CYAN,username,ENDC)

                connections = self.client_roster.presence(username)
                for client, status in connections.items():
                    print(BLUE+'Estado: '+CYAN,status['status'],ENDC)
                print('\n')
        print('-'*25)

    def add_contact(self):
        contact = input("New contact username: ")
        #contact = 'andy@alumchat.xyz'
        self.send_presence_subscription(pto=contact)

    def change_presence(self):
        loop = True
        while(loop):
            print(
                '''
                1. Available
                2. Unavailable
                3. Do not disturb
                '''
            )
            presence = input('Elija un estado: ')
            if presence=='1':
                presence_show = 'chat'
                status = 'Available'
                loop = False
            elif presence == '2':
                presence_show = 'away'
                status = 'Unavailable'
                loop = False
            elif presence=='3':
                presence_show = 'dnd'
                status = 'Do not Disturb'
                loop = False
            else:
                print('Opcion invalida')
        try:
            self.send_presence(pshow=presence_show, pstatus=status)
            logging.info('Presence set')
        except IqError:
            logging.error('Error al enviar presencia')
        except IqTimeout:
            logging.error('No hubo respuesta del servidor')


    def get_message(self, message):
        sender = str(message['from']).split('/')
        print('*'*50)
        print(BLUE+'Mensaje de: '+CYAN,sender[0],ENDC)
        print(CYAN,message['body'],ENDC)
        print('*'*50)
            
    def send_notification(self, recipient, state):
        try:
            notification = self.Message()
            notification["chat_state"] = state
            notification["to"] = recipient

            notification.send()
            logging.info('Se envio la notificacion')
        except IqError:
            logging.error('Problema con notificacion')
        except IqTimeout:
            logging.error('Problema en el servidor')
        
    def receive_notification(self, chatstate):
        # Recibir notificaciones
        sender = str(chatstate['from']).split('/')
        print('*'*50)
        print(BLUE,sender[0],CYAN+ 'is typing',ENDC)
        print('*'*50)

    def sendFile(self):
        with open('./text.txt') as img:
            image = base64.b64encode(img.read()).decode('utf-8')
        self.send_message(mto="andy@alumchat.xyz", mbody=image, msubject='file', mtype='chat')

    async def register(self, iq):

        responce = self.Iq()

        responce['type']='set'
        responce['register']['username'] = self.boundjid.user
        responce['register']['password'] = self.password

        try:
            await responce.send()
            logging.info("Account created")
        except IqError as e:
            logging.error("Could not register account")
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server")
            self.disconnect()

def register(user, password):
    client = Client(user, password)
    client.register_plugin("xep_0030")
    client.register_plugin("xep_0004")
    client.register_plugin("xep_0199")
    client.register_plugin("xep_0066")
    client.register_plugin("xep_0077")

    client['xep_0077'].force_registrarion = True

    client.connect()
    client.process()

def login(username, password):
    client = Client(username, password)
    client.register_plugin("xep_0004") # Data forms
    client.register_plugin("xep_0030") # Service Discovery
    client.register_plugin("xep_0066") # Out-of-band Data
    client.register_plugin('xep_0071') # XHTML-IM
    client.register_plugin("xep_0085") # Chat State Notifications
    client.register_plugin('xep_0128') # Service Discovery Extensions
    client.register_plugin("xep_0199") # XMPP Ping
    client.register_plugin('xep_0045')

    client.connect()
    client.process(forever=False)


#Start Menu
menu = '''
        1. Log In
        2. Sign Up
        3. Quit
        '''

#Start menu loop
start = True

while(start):
    print('*'*50)
    print(menu)
    print('*'*50)

    option = input('Choose an option: ')

    if option=='1': #Log In option
        print('Log In')
        user = input('Write your username (nombre@alumchat.xyz): ')
        password = input('Write your password: ')
        # user='andy@alumchat.xyz'
        # password='12345'
        login(user, password)
    elif option=='2': #Sign Up option
        print('Sign Up')
        username = input('Write your username (nombre@alumchat.xyz): ')
        password = input('Write your password: ')
        # username='pruebaa@alumchat.xyz'
        # password='12345'
        register(username, password)
    elif option=='3': #Quit option
        start = False
    else: #Wrong input
        print(RED+'Invalid Option'+ENDC)


