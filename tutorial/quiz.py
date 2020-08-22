from bs4 import BeautifulSoup
import requests
import random

async def parser():
    page = requests.get("https://europaplus.ru/news/samye-interesnye-fakty-obo-vsem-na-svete")
    full_data = BeautifulSoup(page.text, features="html.parser")
    p_data = full_data.find_all("p", class_="typography typography_type_text typography_size_max typography_mark_light")
    all_facts = [e.get_text().split("\xa0")[0].split(".", 1)[1] if "\xa0" in e.get_text() else e.get_text().split(".", 1)[1] for e in p_data]
    del all_facts[0]
    return all_facts



async def random_fact():
    all_facts = await parser()
    return random.choice(all_facts)