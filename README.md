# Jedha_Kayak_project

La consigne du TP était de collecter les données sur les hôtels dans une cinquantaine de villes en France.

cities = [
"Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence", "Avignon", "Uzes", "Nimes", "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "La Rochelle"]

##Approche choisie :
L'approche choisie a été d'exploiter le template crawl de scrapy via
scrapy genspider -t crawl k2 crawlhotels booking.com
En effet ce template permet de gérer simultanément les liens de chaque hotel et la pagination avec les "rules" : 
        rules = (
            Rule(LinkExtractor(restrict_xpaths= '//h3[contains(@class, "sr-hotel__title")]/a'), callback='parse_item', follow=True),
            Rule(LinkExtractor(restrict_xpaths= '//li[@class="bui-pagination__item bui-pagination__next-arrow"]/a')),
        )

A noter, chaque page "hotel" de type "https://www.booking.com/hotel/fr/the-people-hostel-marseille.fr.html" comporte un script ld+json où l'information est déjà structurée.

On accède aux données du ls+json en affectant le contenu à une variable data
data = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get())

Il suffisait donc de créer un dictionnaire temporaire "microdata" pour y stocker les valeurs contenues dans le ld+json et aussi des points de données indispendables
microdata = {       'user_agent' : str(response.request.headers['User-Agent']), # permet de stocker le user agent utilisé
                    'city' : str(response.request.headers['Referer']),# ville pour jointure avec d'autres données
                    'raw_url' : response.url, #url où les informations sont présentes
                    'company' : data['name'], #point de données dans le script ld+json
                    }
###On a  instancié ItemLoader pour faciliter le cleansing
            l= ItemLoader(item= K2Item(), response = response)
            l.add_value('user_agent', microdata['user_agent'])
            l.add_value('city', microdata['city'])
            l.add_value('raw_url', microdata['raw_url'])
            l.add_value('company', microdata['company'])
            l.add_value('ratingValue', microdata['ratingValue'])

Cette approche permettait donc de scraper d'autres éléments situés dans d'autres noeuds du DOM  comme le montre l'exemple ci-dessous :
            l.add_xpath('wifi', '//*[@data-name-en = "Free WiFi Internet Access Included"]/text()[2]') # infos relatives au wifi
            l.add_xpath('family', '//*[@data-name-en = "Family Rooms"]/text()[2]') # infos relatives au aux chambres pour familles nombreuses
            l.add_xpath('complete_description', '//*[@id="property_description_content"]/child::node()/text()') #description complète de l'hôtel avec une balise enfant
            
            L'ensemble des points de données est retraité dans le fichier items.py avec l'instruction 
            yield l.load_item()
            
##Nettoyage de l'information brute : 
Un autre point tout à fait intéressant est l'utilisation du module itemLoaders qui permet le nettoyage des données brutes qui ont été collectées.
Les fonctions personnalisées dont expliquées dans le fichier items.py
### détermination de l'url canonique
    def short_url(string):
        return re.search("(.*)(?=\?)", string).group(0)

    ####passage des raisons sociales en haut de casse
    def upper(string):
        return string.upper()

    ####Extraction des prix planchers
    def clean_price(string):
        string = ''.join(string)
        return  re.search("[0-9]{1,5}", string).group(0)

    ####Détermination de la latitude et de la longitude dans les urls des cartes
    def geo(string):
        try:
            string = ''.join(string)
            return re.search("(?<=lue%7c)(.+?)(?=&)",string).group(0)
        except:
            return "no data available"

    ####Suppression des sauts de lignes éventuels
    def stripn(string):
        string = ''.join(string)
        return string.strip('\n')

    ####Extraction du libellé de la ville pour jointure (vient de headers['Referrer])
    def get_city(string):
        string = ''.join(string)
        return re.search("(?<=&ss\=)(.+?)(?=&)",string).group(0).replace('%20',' ')

     #### Exemple de nettoyage de l'information brute : 
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

##Note sur l'environnement d'exécution : 
Il a été nécessaire d'importer protego, scrapy, itemLoaders
Le script intégrant la randomisation des user-agents, certaines installations en local se sont avérées complexes dans un environnement local windows 10 (...). 
Nul doute que les commandes suivantes résoudront un certain nombre de difficultés pour d'autres personnes : 
conda install -c anaconda libxml2
conda install -c anaconda requests
conda  install Scrapy-User-Agents



L'export des doonnées se fait en ligne de commande avec l'instruction
scrapy crawl -o data.json
