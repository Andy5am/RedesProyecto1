# XMPP Client
## Author: Andy Castillo (18040)

## Description
The objectives of the project are to learn how to implement and follow the standards from a well known protocol while learning the concepts needed in network development.
In this case we need to implement a client that supports the XMPP protocol.

## Functionalities
The functionalities implemented are:<br/>
* Log in with an account<br/>
* Log out from an account<br/>
* Reguster a new account<br/>
* Delete an account<br/>
* Show all contacts and groups from a user<br/>
* Show the details from a specific user's contact<br/>
* Send and receive private messages<br/>
* Send group messages<br/>
* Change a user status<br/>
* Send and receive notification<br/>
* Send/ and receive file<br/>

## Installation and Usage
**Follow these steps to run the client:**<br/>
```bash
pip install slixmpp
```
```bash
pip install aiohttp
```
```bash
python client.py
```
### Important

The send file funnctionality only works if you use python 3.7 (maybe in lower versions too), 3.8 and above doesn't work.

Sometimes the connection to the server can be difficult.
So if you log in or sign up and nothing shows up after 10 second end the program and run it again.
