import sqlite3
conn = sqlite3.connect('time_bot.db')
c = conn.cursor()

pronouns = []

with open('pronouns.tab') as pronoun_file:
    for line in pronoun_file:
        line = line.strip('\n')
        split = line.split('\t')
        pronouns.append((split[0],split[1],split[2],split[3],split[4]))


c.executemany('INSERT INTO pronouns VALUES (?,?,?,?,?)',pronouns)
conn.commit()
conn.close()
