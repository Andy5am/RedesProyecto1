import logging
import re

import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
class Client(slixmpp.ClientXMPP):

    """
    A basic Slixmpp bot that will log in, send a message,
    and then log out.
    """
    
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.to= 'test@alumchat.xyz'
        self.message= 'Hola'
        # The message we wish to send, and the JID that
        # will receive it.

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('register', self.register)

        self.add_event_handler("message", self.get_message)
        self.add_event_handler("groupchat_message", self.muc_message)

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
        
        def join_group():
            self.plugin['xep_0045'].join_muc('Prueba', 'pruebaa')
        

        
        show = True
        menu = '''
        1. Cerrar Sesion
        2. Eliminar cuenta
        3. Mostrar contactos
        4. Unirse a grupo
        5. Agregar contacto
        6. Detalles contacto
        7. Enviar mensaje a usuario
        8. Enviar mensaje a grupo
        9. Definir presencia
        '''
        while(show):
            print('-'*20)
            print(menu)
            print('-'*20)

            choose = input('Eliga una opcion: ')

            if choose=='1':
                print('Cerrar sesion')
                self.disconnect()
                show = False
            elif choose=='2':
                print('Eliminar cuenta')
                delete_account()
                show = False
            elif choose=='3':
                print('Mostrar contactos')
                self.show_contacts()
            elif choose=='4':
                print('Unir a grupo')
                join_group()
            elif choose=='5':
                print('Agregar contacto')
                self.add_contact()
            elif choose=='6':
                print('Detalles contacto')
                self.show_contact_details()
            elif choose=='7':
                print('Enviar mensaje a usuario')
                self.private_message()
            elif choose=='8':
                print('Enviar mensaje a grupo')
                self.send_group_message()
            elif choose=='9':
                print('Definir presencia')
                self.change_presence()
            else:
                print('Opcion invalida')

            await self.get_roster()

    def send_group_message(self):
        #self.plugin['xep_0045'].join_muc('grupo', 'prueba')
        #group_name = input('Escriba el nombre del grupo: ')
        group_name = 'Prueba'
        #message = input('Escriba el mensaje: ')
        message = 'hola'
        self.send_message(mto=group_name, mbody=message, mtype='groupchat')
    
    def private_message(self):
        recipient = 'andy@alumchat.xyz'
        #message = 'Hola'

        self.send_notification(recipient, "composing")
        # recipient = input('Para quien es el mensaje: ')
        message = input('Cual es el mensaje: ')
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

        #username = input('Ingrese el usuario del contacto: ')
        username = 'andy@alumchat.xyz'

        contact = self.client_roster[username]
        print('-'*40)
        if contact['name']:
            print('Nombre: ',contact['name'],'\n')
        print('Username: ',username,'\n')
        connections = self.client_roster.presence(username)

        if connections=={}:
            print('Estado: Offline')
        else:
            for client, status in connections.items():
                print('Estado: ',status['status'])

        print('-'*40)

    def show_contacts(self):
        groups = self.client_roster.groups()
        
        for group in groups:
            print('-'*25)
            for username in groups[group]:
                name = self.client_roster[username]['name']
                if name:
                    print('Nombre: ',name)
                    print('Usuaio: ',username)
                else:
                    print('Usurio: ',username)

                connections = self.client_roster.presence(username)
                for client, status in connections.items():
                    print('Estado: ',status['status'])
                print('\n')
        print('-'*25)

    def add_contact(self):
        #contact = input("New contact username: ")
        contact = 'andy@alumchat.xyz'
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


    def muc_message(self, message):
        sender = str(message['mucnick']).split('/')
        print('*'*50)
        print('Mensaje de: ',sender[0])
        print(message['body'])
        print('*'*50)


    def get_message(self, message):
        sender = str(message['from']).split('/')
        print('*'*50)
        print('Mensaje de: ',sender[0])
        print(message['body'])
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


    async def register(self, iq):

        responce = self.Iq()

        responce['type']='set'
        responce['register']['username'] = self.boundjid.user
        responce['register']['password'] = self.password

        try:
            await responce.send()
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
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
    client.register_plugin('xep_0045') # Multi-User-Chat

    client.connect()
    client.process(forever=False)



menu = '''
        1. Iniciar Sesion
        2. Registrar cuenta
        3. Salir
        '''

start = True

while(start):
    print('*'*25)
    print(menu)
    print('*'*25)

    option = input('Eliga una opcion: ')

    if option=='1':
        # user = input('Escriba el nombre de usario (nombre@alumchat.xyz): ')
        # password = input('Escriba su contrasena: ')
        user='pruebaa@alumchat.xyz'
        password='12345'
        login(user, password)
    elif option=='2':
        print('Registrar cuenta')
        #username = input('Escriba el nombre de usario (nombre@alumchat.xyz): ')
        #password = input('Escriba su contrasena: ')
        username='pruebaa@alumchat.xyz'
        password='12345'
        register(username, password)
    elif option=='3':
        start = False
    else:
        print('Opcion invalida')


