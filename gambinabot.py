#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tweepy, requests, random, pickle, json
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
    page = requests.get(gambinaPage).text
    soupOfGambinaStores = BeautifulSoup(page, "html.parser")
    last48Stores = []
    storesWithGambina = []
    stores = []
    numberDict = {
        "1": "yksi",
        "2": "kaksi",
        "3": "kolme",
        "4": "neljä",
        "5": "viisi"
	}

    for selectedStore in soupOfGambinaStores.find_all("span",  {"class": "store-in-stock tiny-10 option-text"}):
        storesWithGambina.append(selectedStore.getText())
    storesWithGambina = list(map(lambda s: s.strip(), storesWithGambina))

    storesPage = "https://www.alko.fi/INTERSHOP/web/WFS/Alko-OnlineShop-Site/fi_FI/-/EUR/ALKO_ViewStoreLocator-StoresJSON"
    page = requests.get(storesPage).text
    soupOfStores = BeautifulSoup(page, "html.parser")
    site_json = json.loads(soupOfStores.text)

    for store in site_json["stores"]:
        if store["outletTypeId"] == "outletType_myymalat":
            stores.append(store["name"])

    #Main function for handling the stores, amount of Gambina and forming the tweet
    def main():
        pickle_file = open("gambinafile.pickle", "ab")
        amountOfGambinas = []

        try:
            last48Stores = pickle.load(open("gambinafile.pickle", "rb"))
        except EOFError:
            last48Stores = []

        randomAlko = (random.randint(1, len(stores)-1))
        while stores[randomAlko] in last48Stores:
            randomAlko = (random.randint(1, len(stores)-1))

        if len(last48Stores) < 48:
            last48Stores.append(stores[randomAlko])
            with open ("gambinafile.pickle", "wb") as pickle_file:
                pickle.dump(last48Stores, pickle_file)
        else:
            last48Stores.remove(last48Stores[0])
            last48Stores.append(stores[randomAlko])
            with open ("gambinafile.pickle", "wb") as pickle_file:
                pickle.dump(last48Stores, pickle_file)

        storeString = u'myymälässä '
        selectedGambinaStore = 0
        if stores[randomAlko] in storesWithGambina:
            for gambinaNumber in soupOfGambinaStores.find_all("span", {"class": "right tiny-2 number-in-stock padding-h-0 taste-color"}):
                amountOfGambinas.append(gambinaNumber.getText())

            while stores[randomAlko] != storesWithGambina[selectedGambinaStore]:
                selectedGambinaStore += 1

            storesWithGambina[selectedGambinaStore] = stores[randomAlko]
            amountOfGambinaInSelectedStore = amountOfGambinas[selectedGambinaStore].strip()

            for key in numberDict:
            	if key == amountOfGambinaInSelectedStore:
            		amountOfGambinaInSelectedStore = numberDict[key]

            if amountOfGambinaInSelectedStore == "yksi":
                tweet = "Gambinaa on saatavilla " + amountOfGambinaInSelectedStore + " pullo " + storeString + storesWithGambina[selectedGambinaStore]
            else:
                tweet = "Gambinaa on saatavilla " + amountOfGambinaInSelectedStore + " pulloa " + storeString + storesWithGambina[selectedGambinaStore]
        else:
            tweet = "Gambina on loppu " + storeString + stores[randomAlko] + "!!! :("

        api.update_status(tweet)

    if __name__ == "__main__":
        main()

except Exception as e:
    print(e)