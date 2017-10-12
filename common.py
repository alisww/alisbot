import arrow
import sqlite3
import asyncio
import requests
import re
import api

conn = sqlite3.connect('time_bot.db')
db = conn.cursor()

syntax_message = 'Invalid timezone syntax ): Timezones normally look like this: US/Central. If you don\'t know what is your timezone, you can just go to here: https://alisww.github.io/guesser.html'
usage_message_1 = """
AlisBot, by Alis (https://github.com/alisww)
User data: !register <timezone> # works for updating your timezone too! | !time <user> | !time <timezone> | !register_pronouns <pronouns> | !pronouns <user>
Look-ups: !ud <word> | !urbandictionary <word> # same as !ud | !wikipedia <page title> !pronounis <pronouns> !custom_pronouns <subject> <object> <possesive determiner> <possesive pronoun> <reflexive>
Tool to guess your timezone automatically: https://alisww.github.io/guesser.html
Special channel: #alisbotchannel
Admin commands: !admin_usage"""

admin_usage = """
Admin only commands:
!add_trusted <user> # Adds user to the trusted permission level (allows them to use !ud)
!remove_trusted <user> # Removes user from trusted permission level
!add_admin <user> # Adds user to admin permission level (can add and remove trusted users)
Note: To remove an Admin, the bot creator Alis(sometimes Alis2) should be contacted."""

wikipedia_regex = re.compile('(?:https:|)\/\/(?:\w{2}\.|)(?:m\.|)wikipedia\.org(?:\/wiki|)\/([^\?\n]+)')

def get_hour(timezone):
    try:
        time_ =  arrow.now(timezone).format('HH:mm')
        return time_
    except:
        return None

async def registered_user(user):
    db.execute('INSERT INTO known_users VALUES (?)',(user,))
    conn.commit()

async def match_command(message,target,from_whom,client):
    try:
        wiki_match = wikipedia_regex.match(message)
        print(wiki_match)
        if wiki_match is not None:
            print('wiki!')
            await api.wikipedia(target,client,wiki_match.group(1))

        else:
            message_split = message.split(' ')
            print(message_split)
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

                        row = db.execute('SELECT (timezone) FROM users WHERE user = ?',(user,)).fetchone()
                        if row is not None:
                            time_ = get_hour(row[0])
                            if time_ is not None:
                                await client.say(target,'It\'s {} at {}\'s timezone, {}'.format(time_,user,row[0]))
                            else:
                                await client.say(target,'This user has registered an invalid timezone ):')
                        else:
                            await client.say(target,'This user couldn\'t be found on my database ):')

                elif message_split[0] == '!register':
                    if get_hour(message_split[1]) is not None:
                        if db.execute('SELECT * FROM users WHERE user = ?',(from_whom,)).fetchone() is not None:
                            db.execute('UPDATE users SET timezone = ? WHERE user = ?',(message_split[1],from_whom,))
                            await client.say(target,'Updated your timezone (:')
                        else:
                            db.execute('INSERT INTO users VALUES (?,?)',(from_whom,message_split[1],))
                            db.execute('INSERT INTO known_users VALUES (?)',(from_whom,))
                            await client.say(target,'Registered new timezone (:')
                        conn.commit()
                    else:
                        await client.say(target,syntax_message)

                elif message_split[0] == '!alis_help' or message_split[0] == '!usage':
                    await client.say(target,usage_message_1)
                    time.sleep(2)
                    await client.say(target,usage_message_2)
                    time.sleep(2)
                    await client.say(target,usage_message_3)

                elif message_split[0] == '!ud' or message_split[0] == '!urbandictionary' and message_split[1] is not None:
                    if db.execute('SELECT * FROM known_users WHERE user = ?',(from_whom,)).fetchone() is not None:
                        await api.urban_dictionary(target,client,' '.join(message_split[1:]))
                    else:
                        await client.say(target,'You don\'t have permission to use this command!')

                elif message_split[0] == '!add_trusted' and message_split[1] is not None:
                    if db.execute('SELECT * FROM known_users WHERE user = ?',(message_split[1],)).fetchone() is None:
                        if db.execute('SELECT * FROM admins WHERE user = ?',(from_whom,)).fetchone() is not None:
                            db.execute('INSERT INTO known_users VALUES (?)',(message_split[1],))
                            conn.commit()
                            await client.say(target,'Added user to trusted user list!')
                        else:
                            await client.say(target,'You don\'t have permission to use this command!')
                    else:
                        await client.say(target,'User is already trusted!')

                elif message_split[0] == '!remove_trusted' and message_split[1] is not None:
                    if db.execute('SELECT * FROM known_users WHERE user = ?',(message_split[1],)).fetchone() is not None:
                        if db.execute('SELECT * FROM admins WHERE user = ?',(from_whom,)).fetchone() is not None:
                            db.execute('DELETE FROM known_users WHERE user = ?',(message_split[1],))
                            conn.commit()
                            await client.say(target,'Removed user from trusted users list!')
                        else:
                            await client.say(target,'You don\'t have permission to use this command!')
                    else:
                        await client.say(target,'User is not trusted already!')


                elif message_split[0] == '!add_admin' and message_split[1] is not None:
                    if db.execute('SELECT * FROM admins WHERE user = ?',(message_split[1],)).fetchone() is None:
                        if db.execute('SELECT * FROM admins WHERE user = ?',(from_whom,)).fetchone() is not None:
                            db.execute('INSERT INTO admins VALUES (?)',(message_split[1],))
                            if db.execute('SELECT * FROM known_users WHERE user = ?',(message_split[1],)).fetchone() is None:
                                db.execute('INSERT INTO known_users VALUES (?)',(message_split[1],))
                            conn.commit()
                            await client.say(target,'Added user to admin list!')
                        else:
                            await client.say(target,'You don\'t have permission to use this command!')
                    else:
                        await client.say(target,'User is already an admin!')

                elif message_split[0] == '!admin_usage':
                    if db.execute('SELECT * FROM admins WHERE user = ?',(from_whom,)).fetchone() is not None:
                        await client.say(target,admin_usage)
                    else:
                        await client.say(target,'You don\'t have permission to use this command!')

                elif message_split[0] == '!wikipedia' and message_split[1] is not None:
                    if db.execute('SELECT * FROM known_users WHERE user = ?',(from_whom,)).fetchone() is not None:
                        print('oi')
                        query = ' '.join(message_split[1:])
                        print(query)
                        await api.wikipedia(target,client,query)
                    else:
                        await client.say(target,'You don\'t have permission to use this command!')

                elif message_split[0] == '!pronoun.is' or message_split[0] == '!pronounis':
                    print('pls?')
                    def examples(pronouns):
                        return [
                        '{} drank a cup of tea'.format(pronouns[0].title()),
                        'I hugged {}'.format(pronouns[1]),
                        '{} brought {} tea'.format(pronouns[0].title(),pronouns[2]),
                        'I think that tea was {}'.format(pronouns[3]),
                        '{} asked {}'.format(pronouns[0].title(),pronouns[4])
                        ]

                    if db.execute('SELECT * FROM known_users WHERE user = ?',(from_whom,)).fetchone() is not None:
                        user = db.execute('SELECT (pronouns) FROM users WHERE user = ?',(message_split[1],)).fetchone()
                        if user is not None:
                            print("normal")
                            pronouns_split = user[0].split('/')
                            pronouns = db.execute('SELECT * from pronouns WHERE subject = ? AND object = ?',(pronouns_split[0],pronouns_split[1],)).fetchone()
                            if pronouns[0] is not None:
                                await client.say(target,'How to use {}\'s pronouns, {}:'.format(message_split[1],user[0]))
                                for example in examples(pronouns):
                                    await client.say(target,example)
                            else:
                                await client.say(target,'Couldn\'t find {}\'s pronouns, {} in my pronoun database ): Maybe add it with !custom_pronouns?'.format(message_split[1],user[0]))
                        else:
                            print('Message split[1]:')
                            print(message_split[1])
                            pronouns_split = message_split[1].split('/')
                            print(pronouns_split)
                            pronouns = db.execute('SELECT * from pronouns WHERE subject = ? AND object = ?',(pronouns_split[0],pronouns_split[1],)).fetchone()
                            if pronouns[0] is not None:
                                await client.say(target,'How to use pronouns, {}:'.format(message_split[1]))
                                for example in examples(pronouns):
                                    await client.say(target,example)
                            else:
                                await client.say(target,'Couldn\'t find {} in my pronoun database ): Maybe add it with !custom_pronouns?'.format(message_split[1]))
                    else:
                        await client.say(target,'You don\'t have permission to use this command!')

                elif message_split[0] == '!custom_pronouns' and message_split[5] is not None:
                    db.execute('INSERT INTO pronouns VALUES (?,?,?,?,?)',(message_split[1],message_split[2],message_split[3],message_split[4],message_split[5]))
                    conn.commit()
                    await client.say(target,'Added new custom pronouns!')

                elif message_split[0] == '!pronouns' and message_split[1] is not None:
                    user = db.execute('SELECT (pronouns) FROM users WHERE user = ?',(message_split[1],)).fetchone()
                    if user[0] is not None:
                        await client.say(target,'{}\'s pronouns are {}.'.format(message_split[1],user[0]))
                    else:
                        await client.say(target,'{}\'s pronouns are not registered in my database ): If you didn\'t type a non-existant nickname, you should ask the person what pronouns they prefer and use "they/them/theirs/themselves" in the meantime')

                elif message_split[0] == '!register_pronouns':
                    if db.execute('SELECT * FROM users WHERE user = ?',(from_whom,)).fetchone() is not None:
                        db.execute('UPDATE users SET pronouns = ? WHERE user = ?',(message_split[1],from_whom,))
                        await client.say(target,'Updated your pronouns (:')
                    else:
                        db.execute('INSERT INTO users (user,pronouns) VALUES (?,?)',(from_whom,message_split[1],))
                        db.execute('INSERT INTO known_users VALUES (?)',(from_whom,))
                        await client.say(target,'Registered new pronouns (:')
                    conn.commit()

    except:
        pass

class CommonClient:
    def say(self,target,content):
        return None
