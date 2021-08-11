#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging

import slixmpp

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
class Client(slixmpp.ClientXMPP):

    """
    A basic Slixmpp bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        self.disconnect()

def signup(user, password):
    client = Client(user, password)
    client.register_plugin('xep_0030') # Service Discovery
    client.register_plugin('xep_0004')
    client.register_plugin('xep_0199') # xmpp Ping
    client.register_plugin('xep_0066')
    client.register_plugin('xep_0077')

    client['xep_0077'].force_registrarion = True

    client.connect()
    client.process()

# jid = 'test@alumchat.xyz'
# password = '12345'
# to= 'testw@alumchat.xyz'
# message= 'Hola'

# xmpp = Client(jid, password, to, message)
# xmpp.register_plugin('xep_0030') # Service Discovery
# xmpp.register_plugin('xep_0199') # XMPP Ping

# # Connect to the XMPP server and start processing XMPP stanzas.
# xmpp.connect()
# xmpp.process(forever=False)


menu = '''
        1. Iniciar Sesion
        2. Cerrar Sesion
        3. Registrar cuenta
        4. Eliminar cuenta
        5. Mostrar contactos
        6. Mostrar usuarios
        7. Agregar contacto
        8. Detalles usuario
        9. Enviar mensaje a usuario
        10. Enivar mensaje a todos
        11. Definir presencia
        12. Salir
        '''

start = True

while(start):
    print('-'*25)
    print(menu)
    print('-'*25)

    option = input('Eliga una opcion: ')

    if option=='1':
        user = input('Escriba el nombre de usario (nombre@alumchat.xyz): ')
        password = input('Escriba su contrasena: ')
    elif option=='2':
        print('Cerrar sesion')
    elif option=='3':
        print('Registrar cuenta')
        #username = input('Escriba el nombre de usario (nombre@alumchat.xyz): ')
        #password = input('Escriba su contrasena: ')
        username='pruebaa@alumchat.xyz'
        password='12345'
        signup(username, password)

    elif option=='4':
        print('Eliminar cuenta')
    elif option=='5':
        print('Mostrar contactos')
    elif option=='6':
        print('Mostrar usarios')
    elif option=='7':
        print('Agregar contacto')
    elif option=='8':
        print('Detalles usuario')
    elif option=='9':
        print('Enviar mensaje a usuario')
    elif option=='10':
        print('Enviar mensaje a todos')
    elif option=='11':
        print('Definir presencia')
    elif option=='12':
        start = False
    else:
        print('Opcion invalida')


