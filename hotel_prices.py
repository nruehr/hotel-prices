import requests
import pandas as pd
import json
import os
from os.path import exists
from dotenv import load_dotenv
import datetime as dt

load_dotenv('key.env')
url = os.getenv('HOTEL_URL')

headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": os.getenv('HOTEL_KEY'),
	"X-RapidAPI-Host": os.getenv('HOST_URL')
}

# Global Variables
booking_from = dt.datetime.strptime('2023-12-31', '%Y-%m-%d').date()
booking_until = dt.datetime.strptime('2024-01-01', '%Y-%m-%d').date()
country = 'Japan'
city = 'Tokyo'
no_adults = 1
no_children = 0


# todo: make the booking dates dynamic
def find_hotels(region_id: str):
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": { "regionId": f"{region_id}" },
        "checkInDate": {
            "day": 31,
            "month": 12,
            "year": 2023
        },
        "checkOutDate": {
            "day": 1,
            "month": 1,
            "year": 2024
        },
        "rooms": [
            {
                "adults": 1,
                #"children": [{ "age": 5 }, { "age": 7 }]
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 2,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": { "price": {
                "max": 150,
                "min": 80
            } }
    }
    response = requests.post(url, json=payload, headers=headers)

    print(response.json())
    return response.json()


def write_to_json_file(input):
    json_file = open('data.json', 'w')
    json_file.write(input)
    json_file.close()

# formatted display price looks good
# output one of these jsons to txt
# you can find the region ids on the site
# tokyo = 3593
# you can find the price in 
# object > data > propertyserach > properties > price
# make sure that availability is true!
# there are two prices, which one do you use?
# one of them is before, one of them after discounts

# function to set country
# todo: define a set of city, country, region id tripels that are permitted
def set_country():
    pass


def parse_json(input: str):
    '''Iterate through all prices and return pandas dataframe.'''
    # Find the currency.
    global currency
    currency = input['data']['propertySearch']['properties'][0]['price']['lead']['currencyInfo']['code']

    # Find the number of hotels in the response.
    properties = len(input['data']['propertySearch']['properties'])

    # Build list with all prices and turn it into a dataframe.
    prices = []

    for hotel in range(properties):
        prices.append(round(input['data']['propertySearch']['properties'][hotel]['price']['lead']['amount'], 2))
    prices_df = pd.DataFrame({'price':prices})
    return prices_df


def build_output(prices_df):
    '''Determine values and write to DB.'''
    date = dt.date.today()
    count = prices_df['price'].count()
    mean = round(prices_df['price'].mean(), 2)
    median = round(prices_df['price'].median(), 2)
    min = prices_df['price'].min()
    max = prices_df['price'].max()
    range = round((max - min), 2)
    std = prices_df['price'].std()

    values = [[date, country, city, booking_from, booking_until, no_adults,
               no_children, currency, count, mean, median, min, max, range, std]]

    output = pd.DataFrame(data=values, 
                        columns=['date','country','city','booking_from',
                                'booking_until', 'no_adults', 'no_children',
                                'currency', 'count', 'mean', 'median', 'min', 
                                'max', 'range', 'std'])
    
    # If the output.csv is already there, append the new values.
    if exists('output.csv'):
        csv = pd.read_csv('output.csv')
        csv = pd.concat([csv, output])
        csv.to_csv('output.csv', index=False)
    else:
        output.to_csv('output.csv', index=False)


def update_db():
    input = open('data.json')
    input_json = json.load(input)

    prices_df = parse_json(input=input_json)
    build_output(prices_df=prices_df)


if __name__ == '__main__':
    #resp = find_hotels(region_id = '3593')
    #json_string = json.dumps(resp)
    #write_to_json_file(input=json_string)

    # I need this so I don't have to make the request every time.
    #input = open('data.json')
    #input_json = json.load(input)
    #prices_df = parse_json(input=input_json)
    #build_output(prices_df=prices_df)
    update_db()


    '''
    Locations for the price
    print(input_json['data']['propertySearch']['properties'][0]['price']['displayMessages'][0]['lineItems'][0]['price']['formatted'])
    print(input_json['data']['propertySearch']['properties'][0]['price']['options'][0]['formattedDisplayPrice'])
    print(input_json['data']['propertySearch']['properties'][0]['price']['lead']['amount'])
    print(input_json['data']['propertySearch']['properties'][0]['price']['options'][0]['strikeOut']['formatted'])
    print(input_json['data']['propertySearch']['properties'][0]['price']['options'][0]['strikeOut']['amount'])
    

    # This looks like the best option
    price = round(input_json['data']['propertySearch']['properties'][0]['price']['lead']['amount'], 2)
    print(price)
    '''
    
    '''
    # build the final dataframe
    output = pd.DataFrame(columns=['date','country','city','booking_from',
                               'booking_until', 'currency', 'count', 'mean',
                               'min', 'max', 'std', 'range'])
    '''

