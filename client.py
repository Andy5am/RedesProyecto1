import logging
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

#logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

#Color
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
ENDC = '\033[0m'

#Class wiht al the XMPP functions
class Client(slixmpp.ClientXMPP):
    
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        #Event listeners
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('register', self.register)
        self.add_event_handler("message", self.get_message)
        self.add_event_handler("chatstate_composing", self.receive_notification)

    async def start(self, event):
        #Get contacts and setting status after loging in
        self.send_presence()
        await self.get_roster()

        #Menu after logging in or creating account
        menu = '''
        1. Log Out
        2. Delete Account
        3. Show contacts
        4. Contact Details
        5. Add Contact
        6. Send Private Message
        7. Join Group
        8. Send Group Message
        9. Define Presence
        10. Chat Answers
        '''
        
        #Loop for menu options
        show = True
        while(show):
            print('*'*50)
            print('Bienvenido ',self.jid)
            print(menu)
            print('*'*50)

            choose = input('Choose an option: ')

            #Functions for every option
            if choose == '1':
                print('Log Out')
                self.disconnect()
                show = False
            elif choose == '2':
                print('Delete Account')
                self.delete_account()
                show = False
                print(GREEN+'Account Deleted'+ENDC)
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
                print(GREEN+'Chat Answers'+ENDC)
            else:
                print(RED+'Invalid Option'+ENDC)

            await self.get_roster()

    #Function to delete an account from the server
    def delete_account(self):
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
        
    #Function to join a group chat
    def join_group(self):
        room = input("Write the group name: ")
        nickname = input("write your nickname: ")
        self.plugin['xep_0045'].join_muc(room+"@conference.alumchat.xyz", nickname)
    
    #Function to send a message to a group
    def send_group_message(self):
        room = input("Write the group name: ")
        message = input('Write your message: ')
        self.send_message(mto=room+"@conference.alumchat.xyz", mbody=message, mtype='groupchat')
    
    #Function to send a private message
    def private_message(self):
        recipient = input('Who are you sending the message to (user@alumchat.xyz): ')
        self.send_notification(recipient, "composing")
        message = input('Write your message: ')
        try:
            self.send_notification(recipient, "paused")
            self.send_message(mto=recipient, mbody=message, mtype='chat')
            print(GREEN+'Se envio el mensaje'+ENDC)
        except IqError:
            print(RED+'Error in message send'+ENDC)
        except IqTimeout:
            print(RED+'No server response'+ENDC)

    #Function to show the detail from a specific contact
    def show_contact_details(self):
        self.get_roster()
        username = input('Write the username (user@alumchat.xyz): ')

        contact = self.client_roster[username]
        print('*'*50)
        if contact['name']:
            print(BLUE+'Nombre: '+CYAN, contact['name'],ENDC+'\n')
        print(BLUE+'Username: '+CYAN,username,ENDC+'\n')
        connections = self.client_roster.presence(username)

        if connections=={}:
            print(BLUE+'Estado: Offline'+ENDC)
        else:
            for client, status in connections.items():
                print(BLUE+'Estado: '+CYAN,status['status'],ENDC)

        print('*'*50)

    #Function to show every contact and group
    def show_contacts(self):
        groups = self.client_roster.groups()
        
        for group in groups:
            print('*'*50)
            for username in groups[group]:
                name = self.client_roster[username]['name']
                if username != self.jid:
                    if name:
                        print(BLUE+'Nombre: ',name,ENDC)
                        print(BLUE+'Usuario: '+CYAN,username,ENDC)
                    else:
                        print(BLUE+'Usuario: '+CYAN,username,ENDC)

                    connections = self.client_roster.presence(username)
                    for client, status in connections.items():
                        print(BLUE+'Estado: '+CYAN,status['status'],ENDC)
                    print('\n')
        print('*'*50)

    #Function to add a contact
    def add_contact(self):
        contact = input("New contact username (user@alumchat.xyz): ")
        try:
            self.send_presence_subscription(pto=contact)
            print(GREEN+'Contact Added'+ENDC)
        except:
            print(RED+'Failed to add contact'+ENDC)

    #Function to change the presence
    def change_presence(self):

        #Loop to choose form the different presence options
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
                print(RED+'Opcion invalida'+ENDC)
        try:
            self.send_presence(pshow=presence_show, pstatus=status)
            print(GREEN+'Presence set'+ENDC)
        except IqError:
            print(RED+'Error al enviar presencia'+ENDC)
        except IqTimeout:
            print(RED+'No hubo respuesta del servidor'+ENDC)

    #Function when you receive a message
    def get_message(self, message):
        #When the message received is from a group
        if (message['type']=='groupchat'):
            sender = str(message['from']).split('/')
            print('*'*50)
            print(BLUE+'Grupo: '+CYAN,sender[0],ENDC)
            print(BLUE,sender[1],': '+CYAN,message['body'],ENDC)
            print('*'*50)
        else: #When the message received from a private conversation
            sender = str(message['from']).split('/')
            print('*'*50)
            print(BLUE+'Mensaje de: '+CYAN,sender[0],ENDC)
            print(CYAN,message['body'],ENDC)
            print('*'*50)

    #Function to send notification while typing a message        
    def send_notification(self, recipient, state):
        try:
            notification = self.Message()
            notification["chat_state"] = state
            notification["to"] = recipient

            notification.send()
            print(GREEN+'Se envio la notificacion'+ENDC)
        except IqError:
            print(RED+'Problema con notificacion'+ENDC)
        except IqTimeout:
            print(RED+'Problema en el servidor'+ENDC)
    
    #Function when you receive a notification
    def receive_notification(self, chatstate):
        sender = str(chatstate['from']).split('/')
        print('*'*50)
        print(BLUE,sender[0],CYAN+ 'is typing',ENDC)
        print('*'*50)

    #Function to register a new account to the server from the client menu
    async def register(self, iq):
        responce = self.Iq()
        responce['type']='set'
        responce['register']['username'] = self.boundjid.user
        responce['register']['password'] = self.password

        try:
            await responce.send()
            print(GREEN+"Account created"+ENDC)
        except IqError as e:
            print(RED+"Could not register account"+ENDC)
            self.disconnect()
        except IqTimeout:
            print(RED+"No response from server"+ENDC)
            self.disconnect()

#Function to register a new account from the main menu
def register(user, password):
    client = Client(user, password)
    client.register_plugin("xep_0030") # Service Discovery
    client.register_plugin("xep_0004") # Data Forms
    client.register_plugin("xep_0199") # XMPP Ping
    client.register_plugin("xep_0066") # Out-of-band Data
    client.register_plugin("xep_0077") # In-band Registration
    client.register_plugin('xep_0071') # XHTML-IM
    client.register_plugin("xep_0085") # Chat State Notifications
    client.register_plugin('xep_0128') # Service Discovery Extensions
    client.register_plugin('xep_0045') # Multi user chat

    client['xep_0077'].force_registrarion = True

    client.connect()
    client.process()

#Funtion to log in from the main menu
def login(username, password):
    client = Client(username, password)
    client.register_plugin("xep_0004") # Data forms
    client.register_plugin("xep_0030") # Service Discovery
    client.register_plugin("xep_0066") # Out-of-band Data
    client.register_plugin('xep_0071') # XHTML-IM
    client.register_plugin("xep_0085") # Chat State Notifications
    client.register_plugin('xep_0128') # Service Discovery Extensions
    client.register_plugin("xep_0199") # XMPP Ping
    client.register_plugin('xep_0045') # Multi user chat

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
        login(user, password)
    elif option=='2': #Sign Up option
        print('Sign Up')
        username = input('Write your username (nombre@alumchat.xyz): ')
        password = input('Write your password: ')
        register(username, password)
    elif option=='3': #Quit option
        start = False
    else: #Wrong input
        print(RED+'Invalid Option'+ENDC)


