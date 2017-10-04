import arrow
import sqlite3
import asyncio

conn = sqlite3.connect('time_bot.db')
db = conn.cursor()

syntax_message = 'Invalid timezone syntax ): Timezones normally look like this: US/Central. If you don\'t know what is your timezone, you can just go to here: https://alisww.github.io/guesser.html'

def get_hour(timezone):
    try:
        time = arrow.now(timezone).format('HH:mm')
        return time
    except:
        return None

async def match_command(message,target,from_whom,client):
    try:
        message_split = message.split(' ')
        if message_split[0] is not None:
            if message_split[0] == '!time':
                try_hour = get_hour(message_split[1])
                if try_hour is not None:
                    await client.say(target,'It\'s {} at {}'.format(try_hour,message_split[0]))
                else:
                    user = ""
                    if message_split[1] is not None:
                        user = message_split[1]
                    else:
                        user = from_whom

                    row = db.execute('SELECT * FROM users WHERE user = ?',(user,)).fetchone()
                    if row is not None:
                        time = get_hour(row[1])
                        if time is not None:
                            await client.say(target,'It\'s {} at {}\'s timezone, {}'.format(time,user,row[1]))
                        else:
                            await client.say(target,'This user has registered an invalid timezone ):')
                    else:
                        await client.say(target,'This user couldn\'t be found on my database ):')

            elif message_split[0] == '!register':
                if get_hour(message_split[1]) is not None:
                    if db.execute('SELECT * FROM users WHERE user = ?',(from_whom,)).fetchone() is not None:
                        db.execute('UPDATE users SET timezone = ? WHERE user = ?',(message_split[1],from_whom,))
                    else:
                        db.execute('INSERT INTO users VALUES (?,?)',(from_whom,message_split[1],))
                    conn.commit()
                else:
                    await client.say(target,syntax_message)

            elif message_split[0] == '!alis_help' or message_split[0] == '!usage':
                await client.say(target,"AlisBot, by Alis(https://github.com/alisww)")
                await client.say(target,"Usage:")
                await client.say(target,"!register <timezone> (this works for updating your timezone too!)")
                await client.say(target,"!time <user>")
                await client.say(target,"!time <timezone>")
                await client.say(target,"-------------------")
                await client.say(target,"Tool to guess your timezone automatically: https://alisww.github.io/guesser.html")
    except:
        pass

class CommonClient:
    def say(self,target,content):
        return None
