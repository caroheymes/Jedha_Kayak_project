# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags, replace_escape_chars,strip_html5_whitespace,get_base_url
import re

class K2Item(scrapy.Item):

        # company=scrapy.Field()

    #*************custom functions*****************************
    # détermination de l'url canonique
    def short_url(string):
        return re.search("(.*)(?=\?)", string).group(0)

    #extraction des villes dans les url pour matching
    # def grab_city(string):
    #     string = ''.join(string)
    #     return string.replace("http://booking.com/searchresults.en-gb.html?lang=en-gb&ss=",'').title()

    #passage des raisons sociales en haut de casse
    def upper(string):
        return string.upper()

    #Extraction des prix planchers
    def clean_price(string):
        string = ''.join(string)
        return  re.search("[0-9]{1,5}", string).group(0)

    #Détermination de la latitude et de la longitude dans les urls des cartes
    def geo(string):
        try:
            string = ''.join(string)
            return re.search("(?<=lue%7c)(.+?)(?=&)",string).group(0)
        except:
            return "no data available"

    #Suppression des sauts de lignes éventuels
    def stripn(string):
        string = ''.join(string)
        return string.strip('\n')

    #On a besoin du libellé de la ville pour jointure (vient de headers['Referrer])
    def get_city(string):
        string = ''.join(string)
        return re.search("(?<=&ss\=)(.+?)(?=&)",string).group(0).replace('%20',' ')


    user_agent = scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    city = scrapy.Field(
        input_processor = MapCompose(get_city),
        output_processor = TakeFirst()
    )

    raw_url = scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )

    company=scrapy.Field(
        input_processor = MapCompose(upper),
        output_processor = TakeFirst()
    )
    ratingValue=scrapy.Field(
        input_processor = MapCompose(int),
        output_processor = TakeFirst()
    )
    reviewCount=scrapy.Field(
        input_processor = MapCompose(int),
        output_processor = TakeFirst())
    bestRating=scrapy.Field(
        input_processor = MapCompose(int),
        output_processor = TakeFirst()
    )
    priceRange=scrapy.Field(
        input_processor = MapCompose(clean_price),
        output_processor = TakeFirst()
    )
    description=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    geoloc=scrapy.Field(
        input_processor = MapCompose(geo),
        output_processor = TakeFirst()
    )
    image=scrapy.Field(
        input_processor = MapCompose(get_base_url),
        output_processor = TakeFirst()
    )
    streetAddress=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    addressRegion=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    addressLocality=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    postalCode=scrapy.Field(
        input_processor = MapCompose(int),
        output_processor = TakeFirst()
    )
    hotel_url=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    kind=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    wifi=scrapy.Field(
        input_processor = MapCompose(stripn),
        output_processor = TakeFirst()
    )
    family=scrapy.Field(
        input_processor = MapCompose(stripn),
        output_processor = TakeFirst()
    )
    point_of_interest=scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = TakeFirst()
    )
    complete_description = scrapy.Field(
        input_processor = MapCompose(remove_tags),
        output_processor = Join()
    )
