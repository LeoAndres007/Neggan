import pickle
import logging
from time import ctime

def IrcSend(irc, text):
	irc.send(str.encode(text))

def main(msg, channel, irc,name):
	if msg:
		try:
			flood = open("flood.dat","br")
			nick = pickle.load(flood)
			time = pickle.load(flood)
			flood.close()
			file = True
		except:
			time = 0
			file = False
	
		if not file or nick == name:
			time += 1
			flood = open("flood.dat","bw")
			# Tiempo que tomara el boot para kick por flood - normal 10
			if time == 5:
			# Tiempo que tomara el boot para kick por flood - normal 10
				IrcSend (irc, 'KICK {0} {1} {2}\r\n'.format(channel, name, "flood"))
				# Registro de la expulsion.
				logging.basicConfig(level="logging.INFO")
				logging.info("{0}: {1} make a KICK to {2} becouse {3}".format(ctime(), "|jordan|", name, "flood"))
				time = 0

			pickle.dump(name, flood)
			pickle.dump(time, flood)
			flood.close()
		else:
			time = 1
			flood = open("flood.dat","bw")
			pickle.dump(name, flood)
			pickle.dump(time, flood)
			flood.close()
		
