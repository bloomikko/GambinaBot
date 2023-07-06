#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tweepy
import requests
import random
import pickle
import json
from bs4 import BeautifulSoup

try:
    # Twitter credentials
    # You can get these from https://apps.twitter.com for your account
    CONSUMER_KEY: str = "YOUR_CONSUMER_KEY"
    CONSUMER_SECRET: str = "YOUR_CONSUMER_SECRET"
    ACCESS_KEY: str = "YOUR_ACCESS_KEY"
    ACCESS_SECRET: str = "YOUR_ACCESS_SECRET"

    # Setting up the authentication and API for Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    # Opening the Gambina page with stores and availabilities
    gambina_url: str = "https://www.alko.fi/INTERSHOP/web/WFS/Alko-OnlineShop-Site/fi_FI/-/EUR/ViewProduct-Include?SKU=319027&AppendStoreList=true&AjaxRequestMarker=true"
    page = requests.get(gambina_url).text
    gambina_soup = BeautifulSoup(page, "html.parser")
    last_48_stores: list = []
    stores_with_gambina: list = []
    stores: list = []
    number_dict: dict = {
        "1": "yksi",
        "2": "kaksi",
        "3": "kolme",
        "4": "neljä",
        "5": "viisi",
    }

    for store in gambina_soup.find_all(
        "span", {"class": "store-in-stock tiny-10 option-text"}
    ):
        stores_with_gambina.append(store.getText())
    stores_with_gambina = list(map(lambda s: s.strip(), stores_with_gambina))

    store_page: str = "https://www.alko.fi/INTERSHOP/web/WFS/Alko-OnlineShop-Site/fi_FI/-/EUR/ALKO_ViewStoreLocator-StoresJSON"
    page = requests.get(store_page).text
    stores_soup = BeautifulSoup(page, "html.parser")
    site_json = json.loads(stores_soup.text)

    for store in site_json["stores"]:
        if store["outletTypeId"] == "outletType_myymalat":
            stores.append(store["name"])

    # Main function for handling the stores, amount of Gambina and forming the tweet
    def main():
        pickle_file = open("gambinafile.pickle", "ab")
        number_of_gambinas: list = []

        try:
            last_48_stores: list = pickle.load(open("gambinafile.pickle", "rb"))
        except EOFError:
            last_48_stores: list = []

        random_alko = random.randint(1, len(stores) - 1)
        while stores[random_alko] in last_48_stores:
            random_alko: int = random.randint(1, len(stores) - 1)

        if len(last_48_stores) < 48:
            last_48_stores.append(stores[random_alko])
            with open("gambinafile.pickle", "wb") as pickle_file:
                pickle.dump(last_48_stores, pickle_file)
        else:
            last_48_stores.remove(last_48_stores[0])
            last_48_stores.append(stores[random_alko])
            with open("gambinafile.pickle", "wb") as pickle_file:
                pickle.dump(last_48_stores, pickle_file)

        store_string: str = "myymälässä "
        selected_store: int = 0
        if stores[random_alko] in stores_with_gambina:
            for gambina_number in gambina_soup.find_all(
                "span",
                {"class": "right tiny-2 number-in-stock padding-h-0 taste-color"},
            ):
                number_of_gambinas.append(gambina_number.getText())

            while stores[random_alko] != stores_with_gambina[selected_store]:
                selected_store += 1

            stores_with_gambina[selected_store] = stores[random_alko]
            number_of_gambinas_in_store = number_of_gambinas[selected_store].strip()

            for key in number_dict:
                if key == number_of_gambinas_in_store:
                    number_of_gambinas_in_store = number_dict[key]

            if number_of_gambinas_in_store == "yksi":
                tweet: str = (
                    "Gambinaa on saatavilla "
                    + number_of_gambinas_in_store
                    + " pullo "
                    + store_string
                    + stores_with_gambina[selected_store]
                )
            else:
                tweet: str = (
                    "Gambinaa on saatavilla "
                    + number_of_gambinas_in_store
                    + " pulloa "
                    + store_string
                    + stores_with_gambina[selected_store]
                )
        else:
            tweet: str = (
                "Gambina on loppu " + store_string + stores[random_alko] + "!!! :("
            )

        api.update_status(tweet)

    if __name__ == "__main__":
        main()

except Exception as e:
    print(e)
