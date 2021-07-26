# Jedha_Kayak_project

La consigne du TP était de collecter les données sur le site booking.com sur les hôtels dans une cinquantaine de villes en France.


```python  
cities = [
"Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence", "Avignon", "Uzes", "Nimes", "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "La Rochelle"]
```

## Approche choisie :

L'approche choisie a été d'exploiter le template crawl de scrapy via

```python
scrapy genspider -t crawl k2 crawlhotels booking.com
```

En effet ce template permet de gérer simultanément les liens de chaque hotel et la pagination où  les "rules" sont détaillées ci-dessous : 

```python
        rules = (
            Rule(LinkExtractor(restrict_xpaths= '//h3[contains(@class, "sr-hotel__title")]/a'), callback='parse_item', follow=True),
            Rule(LinkExtractor(restrict_xpaths= '//li[@class="bui-pagination__item bui-pagination__next-arrow"]/a')),
        )
```

## Exploitation des micro-données 

L'exploration des sitemaps et du fichier robot.txt n'a pas permis de mettre en évidence une approche directe. 

A noter, chaque page "hotel" de type "https://www.booking.com/hotel/fr/the-people-hostel-marseille.fr.html" comporte un script *ld+json* où l'information est déjà structurée comme dans l'exemple ci-dessous:
```python

{
   "@context" : "http://schema.org",
   "aggregateRating" : {
      "ratingValue" : 8.5,
      "bestRating" : 10,
      "reviewCount" : 468,
      "@type" : "AggregateRating"
   },
   "url" : "https://www.booking.com/hotel/fr/the-people-hostel-marseille.fr.html",
   "priceRange" : "Tarifs à partir de € 29 par nuit pour les dates à venir (nous ajustons nos tarifs)",
   "name" : "The People Hostel - Marseille",
   "address" : {
      "@type" : "PostalAddress",
      "streetAddress" : "7 rue Jean-Marc Cathala, 13001 Marseille, France",
      "addressLocality" : "7 rue Jean-Marc Cathala",
      "addressRegion" : "Provence-Alpes-Côte d'Azur",
      "postalCode" : "13001",
      "addressCountry" : "France"
   },
   "@type" : "Hotel",
   "hasMap" : "https://maps.googleapis.com/maps/api/staticmap?center=43.3011050,5.3712820&size=1600x1200&sensor=false&zoom=15&markers=color:blue%7c43.3011050,5.3712820&client=gme-booking&channel=booking-frontend&signature=OdWMB7JEoZWsz4XwvxyoG1n8GDg=",
   "image" : "https://cf.bstatic.com/xdata/images/hotel/max500/270127767.jpg?k=bf269a48e8afb82d5600cd7ee20b5fee20d9113a25a5268a53fef503e3380d88&o=&hp=1",
   "description" : "Dotée d’un bar et d’une terrasse, l’auberge de jeunesse The People Hostel - Marseille propose des hébergements à Marseille, à 1 km du centre commercial Les..."
}
```

On accède aux données du ld+json en affectant le contenu à une variable data :
```python
data = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get())
```

Il suffit alors de créer un dictionnaire temporaire "microdata" pour y stocker les valeurs contenues dans le ld+json et d'autres points de données issus de header de la requête (user agent, referrer)
```python
microdata = {       'user_agent' : str(response.request.headers['User-Agent']), # permet de stocker le user agent utilisé
                    'city' : str(response.request.headers['Referer']),# ville pour jointure avec d'autres données
                    'raw_url' : response.url, #url où les informations sont présentes
                    'company' : data['name'], #point de données dans le script ld+json
                    }
```
### On a  instancié ItemLoader pour faciliter le cleansing
```python
            l= ItemLoader(item= K2Item(), response = response)
            l.add_value('user_agent', microdata['user_agent'])
            l.add_value('city', microdata['city'])
            l.add_value('raw_url', microdata['raw_url'])
            l.add_value('company', microdata['company'])
            l.add_value('ratingValue', microdata['ratingValue'])
```

Cette approche permet de collecter d'autres éléments situés dans d'autres noeuds du DOM  comme le montre l'exemple ci-dessous :
```python
            l.add_xpath('wifi', '//*[@data-name-en = "Free WiFi Internet Access Included"]/text()[2]') # infos relatives au wifi
            l.add_xpath('family', '//*[@data-name-en = "Family Rooms"]/text()[2]') # infos relatives au aux chambres pour familles nombreuses
            l.add_xpath('complete_description', '//*[@id="property_description_content"]/child::node()/text()') #description complète de l'hôtel avec une balise enfant
 ```
            
L'ensemble des points de données est retraité dans le fichier items.py avec la méthode 
 ```python
            yield l.load_item()
```            
            
## Nettoyage de l'information brute : 

Un autre point tout à fait intéressant est l'utilisation du module itemLoaders qui permet le nettoyage des données brutes.
Il est nécessaire d'importer certains modules dans ce fichier : 
```python
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags, replace_escape_chars,strip_html5_whitespace,get_base_url
import re
```

Les fonctions personnalisées du fichier items.py permettent un nettoyage plus robuste des données comme le montrent les exemples ci-dessous


#### détermination de l'url canonique
```python
    def short_url(string):
        return re.search("(.*)(?=\?)", string).group(0)
```

#### passage des raisons sociales des hôtels en haut de casse
```python
    def upper(string):
        return string.upper()
```

#### Extraction des prix planchers
```python
l'information brute est du type
"priceRange" : "Tarifs à partir de € 29 par nuit pour les dates à venir (nous ajustons nos tarifs)"

    def clean_price(string):
        string = ''.join(string)
        return  re.search("[0-9]{1,5}", string).group(0)
```

#### Détermination de la latitude et de la longitude dans les urls des cartes
```python
    def geo(string):
        try:
            string = ''.join(string)
            return re.search("(?<=lue%7c)(.+?)(?=&)",string).group(0)
        except:
            return "no data available"
```

#### Suppression des sauts de lignes éventuels
```python
    def stripn(string):
        string = ''.join(string)
        return string.strip('\n')
```

#### Extraction du libellé de la ville pour jointure (vient de headers['Referrer])
```python
    def get_city(string):
        string = ''.join(string)
        return re.search("(?<=&ss\=)(.+?)(?=&)",string).group(0).replace('%20',' ')
```

#### Exemples de nettoyage de l'information brute : 
```python
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
```

## Note sur l'environnement d'exécution : 

Il a été nécessaire d'importer protego, scrapy, itemLoaders
Le script intégrant la randomisation des user-agents, certaines installations en local se sont avérées complexes dans un environnement local windows 10 (...). 
Nul doute que les commandes suivantes résoudront un certain nombre de difficultés pour d'autres personnes qui voudront ré-utiliser le code: 
```python
conda install -c anaconda libxml2
conda install -c anaconda requests
conda  install Scrapy-User-Agents
```

## Export de données
L'export des doonnées se fait en ligne de commande avec l'instruction
```python
crapy crawl crawlhotels -o data.json
```
