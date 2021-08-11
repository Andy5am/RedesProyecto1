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

    async def start(self, event):
        self.send_presence()

        def send_message():
            recipient = 'andy@alumchat.xyz'
            message = 'Hola'

            # recipient = input('Para quien es el mensaje: ')
            # message = input('Cual es el mensaje: ')

            self.send_message(mto=recipient, mbody=message, mtype='chat')
            print('Se envio el mensaje')
        
        def add_contact():
            #contact = input("New contact username: ")
            contact = 'andy@alumchat.xyz'
            self.send_presence_subscription(pto=contact)

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
        1. Cerrar Sesion
        2. Eliminar cuenta
        3. Mostrar contactos
        4. Mostrar usuarios
        5. Agregar contacto
        6. Detalles usuario
        7. Enviar mensaje a usuario
        8. Enviar mensaje a todos
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
            elif choose=='4':
                print('Mostrar usuarios')
            elif choose=='5':
                print('Agregar contacto')
                add_contact()
            elif choose=='6':
                print('Detalles usuario')
            elif choose=='7':
                print('Enviar mensaje a usuario')
                send_message()
            elif choose=='8':
                print('Enviar mensaje a todos')
            elif choose=='9':
                print('Definir presencia')
            else:
                print('Opcion invalida')

            await self.get_roster()
        

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
    client.register_plugin("xep_0030")
    client.register_plugin("xep_0199")

    client.connect()
    client.process(forever=False)



menu = '''
        1. Iniciar Sesion
        2. Registrar cuenta
        3. Salir
        '''

start = True

while(start):
    print('-'*25)
    print(menu)
    print('-'*25)

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


