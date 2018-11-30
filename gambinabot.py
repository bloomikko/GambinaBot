#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tweepy, urllib2, random, pickle
from bs4 import BeautifulSoup

try:
	#Twitter credentials, you can get these from https://apps.twitter.com for your account
	CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
	CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
	ACCESS_KEY = 'YOUR_ACCESS_KEY'
	ACCESS_SECRET = 'YOUR_ACCESS_SECRET'

	#Setting up the authentication and API for Twitter
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
	api = tweepy.API(auth)

	#Opening the Gambina page with stores and availabilities
	gambinaPage = "https://www.alko.fi/INTERSHOP/web/WFS/Alko-OnlineShop-Site/fi_FI/-/EUR/ViewProduct-Include?SKU=319027&AppendStoreList=true&AjaxRequestMarker=true"
	page = urllib2.urlopen(gambinaPage)
	soup = BeautifulSoup(page, 'html.parser')
	last48Stores = []
	stores = []

	gambinaRequest = urllib2.urlopen(gambinaPage)
	gambinaSoup = BeautifulSoup(gambinaRequest, 'html.parser')

	for selectedStore in gambinaSoup.find_all('span',  {"class": "store-in-stock tiny-10 option-text"}):
		stores.append(selectedStore.getText())
	stores = map(lambda s: s.strip(), stores)	
	
	#Main function for handling the stores, amount of Gambina and forming the tweet
	def main():
		pickle_file = open('gambinafile.pickle', 'ab')
		amountOfGambinas = []

		try:
			last48Stores = pickle.load(open('gambinafile.pickle', 'rb'))
		except EOFError:
			last48Stores = []

		randomAlko = (random.randint(1, len(stores)-1))
		while randomAlko in last48Stores:
			randomAlko = (random.randint(1, len(stores)-1))

		if len(last48Stores) < 48:
			last48Stores.append(randomAlko)
			with open ('gambinafile.pickle', 'wb') as pickle_file:
				pickle.dump(last48Stores, pickle_file)
		else:
			last48Stores.remove(last48Stores[0])
			last48Stores.append(randomAlko)
			with open ('gambinafile.pickle', 'wb') as pickle_file:
				pickle.dump(last48Stores, pickle_file)

		for selectedStoreGambinaAmount in gambinaSoup.find_all('span',  {"class": "right tiny-2 number-in-stock padding-h-0 taste-color "}):
			amountOfGambinas.append(selectedStoreGambinaAmount.getText())

		amountOfGambinaInSelectedStore = amountOfGambinas[randomAlko]
		storeString = u'myymälässä '
		if amountOfGambinaInSelectedStore == "1":
			tweet = "Gambinaa on saatavilla " + amountOfGambinaInSelectedStore + " pullo " + storeString + stores[randomAlko]
		else:
			tweet = "Gambinaa on saatavilla " + amountOfGambinaInSelectedStore + " pulloa " + storeString + stores[randomAlko]

		api.update_status(tweet)
		print(tweet)

	if __name__ == "__main__":
		main()

except Exception as e:
    print(e.message)