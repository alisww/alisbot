import requests
import wikipedia
from bs4 import BeautifulSoup
import asyncio

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

async def wikipedia(target,client,query,lang='en'):
    if lang is None:
        lang = 'en'

    wikipedia.set_language(lang)

    try:
        page = wikipedia.summary(query)
        for part in page.split('\n')[0].split('.'):
            await client.say(target,part + '.')
    except wikipedia.exceptions.DisambiguationError as e:
        await client.say(target,'Found more than one option: {}'.format(','.join(e.options)))
    except wikipedia.exceptions.PageError as e:
        await client.say(target,'Couldn\'t find page {} ):'.format(query))

async def pronounis(target,client,pronouns):
    r = requests.get('http://pronoun.is/{}'.format(pronouns))
    soup = BeautifulSoup(r.text)
    examples = soup.find_all(class_="sentence")
    print(examples)
    if len(examples) > 0:
        await client.say(target,'How to use the pronouns {}:'.format(pronouns))
        for example in examples:
            await client.say(target,example.text)
