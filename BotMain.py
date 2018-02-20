# Developed by Rafik Mas'ad (Azag).
# AzagBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# AzagBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Importar modulos 
import socket
import logging
import os
from time import ctime
import plugin
import configparser


version = 9.07

# Funcion que extrae el nombre del usuario.
def get_name(data, channel):
	try:
		return data[1:data.find("!")]
	except:
		return False

# Funcion que extrae el nombre del usuario.
def get_user(data, channel):
	try:
		return data[data.find("!n=") + 3:data.find("@")]
	except:
		return False

# Funcion que extrae el mensaje
def get_msg(data, channel):
	if 'PRIVMSG {0} :'.format(channel) in data:
		msg_start = data.find('PRIVMSG {0} :'.format(channel))
		msg_start += len('PRIVMSG {0} :'.format(channel))
		if data[msg_start:].strip() == " ":
			return "Blank"
		return data[msg_start:].strip()
	return False

# Funcion que extrae el aviso
def get_advice(data, channel, name):
	if not 'freenode' in data:
		if 'JOIN' in data:
			return ('JOIN', 'None')
		if 'PART' in data:
			return ('QUIT', 'None')
		if 'QUIT' in data:
			return ('QUIT', 'None')
		if 'KICK' in data:
			advice_start = data.find('KICK {0} '.format(channel))
			advice_start += len('KICK {0} '.format(channel))
			advice_end = data.find(' :')
			return ('KICK', data[advice_start:advice_end])
	return (False, 'None')

# Funcion que combierte el string en bytes y envia el texto.
def IrcSend(irc, text):
	irc.send(str.encode(text))

# Funcion para sacar (kick) a alguien del canal
def kick(msg, name, channel, irc):
	end_name = msg.find(" ")
	IrcSend (irc, 'KICK {0} {1}\r\n'.format(channel, msg[6:end_name]))
	# Registro de la expulsion.
	logging.basicConfig(level="logging.INFO")
	logging.info("{0}: {1} make a KICK to {2} becouse {3}".format(ctime(), name, msg[6:end_name]), msg[end_name:])

# Funcion principal
def main(nick, channel, irc):
	try:
		# Get information from the config file
		config = configparser.RawConfigParser()
		config.read('config.cfg')

		OPs = config.get('Channel members', 'OPs')
		womans = config.get('Channel members', 'womans')
        
		data = bytes.decode(irc.recv (4096))
		print (data)

		name = get_name(data, channel)
		user = get_user(data, channel)
		msg = get_msg(data, channel)
		if not msg:
			advice, was_kick = get_advice(data, channel, name)
		else:
			advice, was_kick = False, 'None'
		
		if 'PRIVMSG {0}'.format(nick) in data:
			IrcSend(irc, "PRIVMSG {0} :No acepto mensajes privados.".format(name))
			raise ValueError()
		
		response = {'hola {0}'.format(nick.lower()): 'Hola we {0}\r\n'.format(name),
					'hi {0}'.format(nick.lower()): 'Hi {0}\r\n'.format(name),
					'ping': 'pong\r\n',
					'#list': 'Mi listado de comandos {0}: hi #Neggan#, ping, #Neggan#, #wiki, #portal, #paste, #v, #version, #op, #list, #deop, hola #Neggan#, bot, #chao, #math en el canal {1}\r\n'.format(name, channel),					
					'#Neggan#,': ':#\r\n',
					'bot': ':s\r\n',
					'bot,': ':s\r\n',
					'#Neggan#': ':#\r\n',
					'#wiki': '"wiki" - es.wikipedia.com/\r\n',
					'#portal': '"portal" - Nueva Pagina: https://Gatewayrd.mipropia.com\r\n',
					'#paste': '"paste" - https://pastebin.com\r\n',
					'#v': 'Neggan versión {0}\r\n'.format(version),
					'#version': 'Neggan versión {0}\r\n'.format(version)}
		
		op_response = {'#kick {0}'.format(was_kick): 'El usuario {0} ha sido expulsado por mi\r\n'.format(was_kick),
					   '#op': 'El usuario {0} ahora es operador de {1}\r\n'.format(name, channel),
					   '#deop': 'El usuario {0} ya no es operador de {1}\r\n'.format(name, channel),
					   #'#list': 'Mi listado de comandos {0}: hi #Neggan#, ping, #Neggan#, #wiki, #portal, #paste, #v, #version, #op, #list, #deop, hola #Neggan#, bot, #chao, #math en el canal {1}\r\n'.format(name, channel),
					   '#chao': 'Adios :v de {0}.\r\n'.format(channel)}	

		if msg:
			if user in OPs:
				if msg == '#chao':
					IrcSend (irc, "QUIT [Gatewayrd] {0}\r\n".format(version))
					exit()
				# No da kick.
				if '¬kick' in msg:
				# No da kick.
					kick(msg, name, channel, irc)
						
				if msg == '#op':
					IrcSend (irc, "MODE {0} +o {1}\r\n".format(channel, name))

				if msg == '#deop':
					IrcSend (irc, "MODE {0} -o {1}\r\n".format(channel, name))
								
				if msg.lower() in op_response:
					IrcSend(irc, "PRIVMSG {0} :{1}".format(channel, op_response[msg.lower()]))
				
			if msg.lower() in response:
				IrcSend(irc, "PRIVMSG {0} :{1}".format(channel, response[msg.lower()]))

		if advice == 'KICK':
			if was_kick == nick:
				IrcSend (irc, "JOIN {0}\r\n".format(channel))
				IrcSend (irc, "PRIVMSG ChanServ :OP {0}\r\n".format(channel))

		if advice == "JOIN" and name != nick:
			if name not in womans:
				IrcSend (irc, "PRIVMSG {0} :Hola Bienvenid@ :) {1}\r\n".format(channel, name))
			if name in womans:
				IrcSend (irc, "PRIVMSG {0} :Hola Bienvenid@ :) {1}\r\n".format(channel, name))
		
		plugin.main(name, msg, user, advice, channel, irc)

	except UnicodeDecodeError:
		logging.basicConfig(level="logging.ERROR")
		logging.error("{0}: UnicodeDecodeError".format(ctime()))
	
	except ValueError:
		logging.basicConfig(level="logging.WARNING")
		logging.warning("{0}: Private msg send by {1} (User: {2})".format(ctime(), name, user))
