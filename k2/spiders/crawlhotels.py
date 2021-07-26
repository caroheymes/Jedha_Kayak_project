import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import K2Item
import json
from scrapy.loader import ItemLoader

# https://github.com/orangain/scrapy-s3pipeline


class CrawlhotelsSpider(CrawlSpider):
    name = 'crawlhotels'
    allowed_domains = ['booking.com']
    # start_urls =['http://booking.com/searchresults.en-gb.html?lang=en-gb&ss=Bayeux'
    # ,'http://booking.com/searchresults.en-gb.html?lang=en-gb&ss=Saint Malo'
    # ]
    cities = ["Mont Saint Michel",
    "Saint Malo",
    "Bayeux",
    "Le Havre",
    "Rouen",
    "Paris",
    "Amiens",
    "Lille",
    "Strasbourg",
    "Chateau du Haut Koenigsbourg",
    "Colmar",
    "Eguisheim",
    "Besancon",
    "Dijon",
    "Annecy",
    "Grenoble",
    "Lyon",
    "Gorges du Verdon",
    "Bormes les Mimosas",
    "Cassis",
    "Marseille",
    "Aix en Provence",
    "Avignon",
    "Uzes",
    "Nimes",
    "Aigues Mortes",
    "Saintes Maries de la mer",
    "Collioure",
    "Carcassonne",
    "Ariege",
    "Toulouse",
    "Montauban",
    "Biarritz",
    "Bayonne",
    "La Rochelle"
    ]
    start_urls = []
    for city in cities:
        start_urls.append('http://booking.com/searchresults.en-gb.html?lang=en-gb&ss=' + city)
    #
    for k,v in enumerate(start_urls):

        rules = (
            Rule(LinkExtractor(restrict_xpaths= '//h3[contains(@class, "sr-hotel__title")]/a'), callback='parse_item', follow=True),
            Rule(LinkExtractor(restrict_xpaths= '//li[@class="bui-pagination__item bui-pagination__next-arrow"]/a')),
        )

        def parse_item(self, response):
            data = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get())
            #Easy set-up

            # wifi = response.xpath('//*[@data-name-en = "Free WiFi Internet Access Included"]/text()[2]').get()
            # family = response.xpath('//*[@data-name-en = "Family Rooms"]/text()[2]').get()
            # point_of_interest = response.xpath('//h3[@class="bui-card__title"]/text()').get()
            # complete_description = response.xpath('//*[@id="property_description_content"]/child::node()/text()').getall()


            # items = {
            #         'wifi' :  wifi,
            #         'family' : family,
            #         'point_of_interest' :  point_of_interest,
            #         'complete_description': complete_description}
            # yield items

            '''
            On collecte d'abord les points de données dans le script ld+json
            de chaque page html d'hôtel ainsi que des données additionnelles du header comme le user_agent
            et le Referrer pour récupérer la ville de base
            '''
            microdata = {
                    'user_agent' : str(response.request.headers['User-Agent']),
                    'city' : str(response.request.headers['Referer']),
                    'raw_url' : response.url,
                    'company' : data['name'],
                    'ratingValue' : data['aggregateRating']['ratingValue'],
                    'reviewCount' : data['aggregateRating']['reviewCount'],
                    'bestRating' : data['aggregateRating']['bestRating'],
                    'priceRange' : data['priceRange'],
                    'description' : data['description'],
                    'geoloc' : data['hasMap'],
                    'image' : data['image'],
                    'streetAddress' : data['address']['streetAddress'],
                    'addressRegion' : data['address']['addressRegion'],
                    'addressLocality' : data['address']['addressLocality'],
                    'postalCode' : data['address']['postalCode'],
                    'hotel_url' : data['url'],
                    'kind' : data['@type'],
                    }

            #On instancie ItemLoader pour faciliter le cleansing
            l= ItemLoader(item= K2Item(), response = response)
            l.add_value('user_agent', microdata['user_agent'])
            l.add_value('city', microdata['city'])
            l.add_value('raw_url', microdata['raw_url'])
            l.add_value('company', microdata['company'])
            l.add_value('ratingValue', microdata['ratingValue'])
            l.add_value('reviewCount', microdata['reviewCount'])
            l.add_value('bestRating', microdata['bestRating'])
            l.add_value('priceRange', microdata['priceRange'])
            l.add_value('description', microdata['description'])
            l.add_value('geoloc', microdata['geoloc'])
            l.add_value('image', microdata['image'])
            l.add_value('streetAddress', microdata['streetAddress'])
            l.add_value('addressRegion', microdata['addressRegion'])
            l.add_value('addressLocality', microdata['addressLocality'])
            l.add_value('postalCode', microdata['postalCode'])
            l.add_value('hotel_url',microdata['hotel_url'])
            l.add_value('kind', microdata['kind'])
            '''
            On ajoute les données accessibles uniquement par xpath
            '''
            l.add_xpath('wifi', '//*[@data-name-en = "Free WiFi Internet Access Included"]/text()[2]')
            l.add_xpath('family', '//*[@data-name-en = "Family Rooms"]/text()[2]')
            l.add_xpath('point_of_interest', '//h3[@class="bui-card__title"]/text()')
            l.add_xpath('complete_description', '//*[@id="property_description_content"]/child::node()/text()')


            yield l.load_item()
