import requests
from bs4 import BeautifulSoup
import asyncio
import urllib

async def urban_dictionary(target,client,query):
    r = requests.get("http://api.urbandictionary.com/v0/define",params={'term': query}).json()

    try:

        if 'error' not in r:

            await client.say(target,"{}: {}".format(r['list'][0]['word'],r['list'][0]['definition']))
            await client.say(target,"Example: {}".format(r['list'][0]['example']))

        else:
            await client.say(target,"Got error from UrbanDictionary: {}".format(r['error']))

    except IndexError:
        await client.say(target,"Got no results ):")

async def wikipedia(target,client,query):
    query = urllib.parse.quote(query.replace(' ','_'))
    print(query)
    try:
        r = requests.get('https://en.m.wikipedia.org/wiki/{}?prop=extracts&exsectionformat=plain'.format(query),timeout = 2)
        r.raise_for_status()
        print(r)
        soup = BeautifulSoup(r.text)
        for part in soup.find(id='mf-section-0').find('p').text.split('.'):
            await client.say(target,part.strip('\n') + '.')
    except:
        await client.say(target,'Couldn\'t get page from wikipedia ):')
