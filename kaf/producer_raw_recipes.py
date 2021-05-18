import requests
from time import sleep
from bs4 import BeautifulSoup
from kafka import KafkaProducer

def fetch_raw(recipe_url):
    html = None
    print('Processing..{}'.format(recipe_url))
    try:
        r = requests.get(recipe_url, headers=headers)
        if r.status_code == 200:
            html = r.text
    except Exception as ex:
        print('Exception while accessing raw html')
        print(str(ex))
    finally:
        return html.strip()


def get_recipes(headers):
    recipes = []
    salad_url = 'https://www.allrecipes.com/recipes/96/salad/'
    url = 'https://www.allrecipes.com/recipes/96/salad/'
    print('Accessing list')
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            links = soup.findAll("a", href=True)
            for link in links:
               hReF = link["href"]
               split_ref = hReF.split("https://")
               if len(split_ref) > 1:
                    if ".com" in split_ref[1]:
                        recipes.append(hReF)
    except Exception as ex:
        print('Exception in get_recipes')
        print(str(ex))
    finally:
        print("list of recipes found. example element : ", recipes[0])
        return recipes

def publish_message(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding='utf-8')
        print("key_bytes : ", key_bytes) 
        value_bytes = bytes(value, encoding='utf-8')
        print("value_bytes : ", value_bytes)
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=['localhost:9092'], api_version=(0, 10))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Pragma': 'no-cache'
    }
    all_recipes = ["https://www.allrecipes.com/recipe/20762/california-coleslaw/", "https://www.allrecipes.com/recipe/8584/holiday-chicken-salad/", "https://www.allrecipes.com/recipe/80867/cran-broccoli-salad/"]
#    all_recipes = get_recipes(headers)
    if len(all_recipes) > 0:
        print("connecting to producer. . .")
        kafka_producer = connect_kafka_producer()
        print("connected to producer")
        for recipe in all_recipes:
            print("publishing recipe for : ", recipe)
            publish_message(kafka_producer, 'raw_recipes', 'raw', recipe.strip())
        if kafka_producer is not None:
            print("closing . . .")
            kafka_producer.close()
