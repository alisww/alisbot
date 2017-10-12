import socket
import sched,time
import common
import asyncio
import re
import sys

registered_regex = re.compile("Information on (.*) \(account .*\):")

class IRCClient(common.CommonClient):

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def connect(self,server,channels):
        self.irc.connect((server,6667))
        self.irc.send(bytes('USER AlisBot 8 * :AlisBot\n','UTF-8'))
        self.irc.send(bytes('NICK AlisBot \n','UTF-8'))
        print(self.irc)
        print("Connected.")

        self.channels = channels
        self.server = server

        s = sched.scheduler(time.time,time.sleep)
        for (idx,channel) in enumerate(channels):
            s.enter(10 + idx,1,self.join_channel,argument=(channel,))

        s.run()

    def join_channel(self,channel):
        self.irc.send(bytes('JOIN {} \n'.format(channel),'UTF-8'))

    def ping(self):
        self.irc.send(bytes('PONG :pingis \n','UTF-8'))

    async def say(self,target,content):
        for message in content.split('\n'):
            self.irc.send(bytes('PRIVMSG {} :{} \n'.format(target,message),'UTF-8'))

    async def registered(self,target,content):
        match = registered_regex.match(content).group(1)
        if match is not None:
            await common.registered_user(match)

    async def query_nickserv(self,user):
        self.irc.send(bytes('PRIVMSG NICKSERV :INFO {}'.format(user),'UTF-8'))

    async def run(self):
        message = self.irc.recv(2048).decode('UTF-8').strip('\n\r')
        if message:
            sys.stdout.buffer.write(message.encode('utf-8'))
            if message.find('PRIVMSG') != -1:
                name = message.split('!',1)[0][1:]
                content = message.split(':')[-1]
                target = message.split('PRIVMSG',1)[1].split(':',1)[0]

                if name == "NickServ":
                    #await self.registered(target,content,name)
                    pass
                else:
                    await common.match_command(content,target,name,self)
            elif message.find('PING :') != -1:
                self.ping()

            elif message.find('JOIN') != -1:
                name = message.split('!',1)[0][1:]
                #await self.query_nickserv(name)

        else:
            self.connect(self.server,self.channels)

client = IRCClient()
client.connect('irc.blitzed.org',[])


loop = asyncio.get_event_loop()
loop.run_until_complete(client.say('NickServ','identify '))
while True:
    loop.run_until_complete(client.run())

loop.close()
