class countries():
    def __init__(self):
        self.european_countries = {
            "Albania": "albania.png",
            "Andorra": "andorra.png",
            "Armenia": "armenia.png",
            "Austria": "austria.png",
            "azerbaijan": "azerbaijan.png",
            "belarus": "belarus.png",
            "belgium": "belgium.png",
            "bosnia and herzegovina": "bosnia and herzegovina.png",
            "bulgaria": "bulgaria.png",
            "croatia": "croatia.png",
            "cyprus": "cyprus.png",
            "czech republic": "czech republic.png",
            "denmark": "denmark.png",
            "estonia": "estonia.png",
            "finland": "finland.png",
            "germany": "germany.png",
            "France": "france.png",
            "georgia": "georgia.png",
            "greece": "greece.png",
            "hungary": "hungary.png",
            "iceland": "iceland.png",
            "ireland": "ireland.png",
            "Italy": "italy.png",
            "latvia": "latvia.png",
            "liechtenstein": "liechtenstein.png",
            "lithuania": "lithuania.png",
            "luxembourg": "luxembourg.png",
            "malta": "malta.png",
            "moldova": "moldova.png",
            "monaco": "monaco.png",
            "montenegro": "montenegro.png",
            "netherlands": "netherlands.png",
            "north macedonia": "north macedonia.png",
            "norway": "norway.png",
            "poland": "poland.png",
            "portugal": "portugal.png",
            "romania": "romania.png",
            "russia": "russia.png",
            "san marino": "san marino.png",
            "serbia": "serbia.png",
            "slovakia": "slovakia.png",
            "slovenia": "slovenia.png",
            "spain": "spain.png",
            "sweden": "sweden.png",
            "switzerland": "switzerland.png",
            "turkey": "turkey.png",
            "ukraine": "ukraine.png",
            "united kingdom": "united kingdom.png",
            "vatican city": "vatican city.png",
        }
        self.american_countries  = {
            "united states of america": "united states of america.png"
        }
        self.asian_countries = {}
        self.oceanic_countries = {}
        self.african_countries = {}
        self.result = {}
    def getResult(self):
        if self.european_countries:
            self.result.update(self.european_countries)
        if self.american_countries:
            self.result.update(self.american_countries)
        if self.asian_countries:
            self.result.update(self.asian_countries)
        if self.oceanic_countries:
            self.result.update(self.oceanic_countries)
        if self.african_countries:
            self.result.update(self.african_countries)

        return self.result