import socket
import sched,time
import common
import asyncio

class IRCClient(common.CommonClient):

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def connect(self,server,channels):
        self.irc.connect((server,6667))
        self.irc.send(bytes('USER AlisBot 8 * :AlisBot\n','UTF-8'))
        self.irc.send(bytes('NICK AlisBot \n','UTF-8'))
        print(self.irc)
        print("Connected.")

        for channel in channels:
            self.join_channel(channel)

    def join_channel(self,channel):
        self.irc.send(bytes('JOIN {} \n'.format(channel),'UTF-8'))

    def ping(self):
        self.irc.send(bytes('PONG :pingis \n','UTF-8'))

    async def say(self,target,content):
        self.irc.send(bytes('PRIVMSG {} :{} \n'.format(target,content),'UTF-8'))

    async def run(self):
        message = self.irc.recv(2048).decode('UTF-8').strip('\n\r')
        if message.find('PRIVMSG') != -1:
            name = message.split('!',1)[0][1:]
            content = message.split(':')[-1]
            target = message.split('PRIVMSG',1)[1].split(':',1)[0]
            await common.match_command(content,target,name,self)
        elif message.find('PING :') != -1:
            self.ping()

client = IRCClient()
client.connect('irc.blitzed.org',['#yayforqueers'])

s = sched.scheduler(time.time,time.sleep)
s.enter(10,1,client.join_channel,argument=("#yayforqueers",))
s.enter(11,1,client.join_channel,argument=("#queerscouts",))
s.run()

loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(client.run())

loop.close()
