import json
from urllib import quote

class Localizer:
    def __init__(self, lang):
        filename = "languages/" + lang + ".json"
        fh = open(filename, 'r')
        try:
            self.values = json.load(fh)
            for key in self.values.keys():
                self.values[key] = self.values[key].encode('utf-8')
        finally:
            fh.close()

        filename = "custom/default.json"
        fh = open(filename, 'r')
        try:
            customs = json.load(fh)
            for key in customs.keys():
                # encode and save into previous dictionary
                self.values[key] = customs[key].encode('utf-8')
        finally:
            fh.close()

        filename = "custom/aliases.json"
        fh = open(filename, 'r')
        try:
            self.aliases = json.load(fh)
            for key in self.aliases.keys():
                self.aliases[key] = self.aliases[key].encode('utf-8')
        finally:
            fh.close()

        filename = "custom/donations.json"
        fh = open(filename, 'r')
        try:
            self.donations = json.load(fh)
        finally:
            fh.close()

    def addPageVariables(self, author, search, search_from, search_to, order, page):
        self.values["author"] = author
        self.values["author-quoted"] = quote(author)
        self.values["search"] = search
        self.values["search-quoted"] = quote(search)
        self.values["search_from"] = search_from
        self.values["search_to"] = search_to
        self.values["order"] = order
        self.values["page"] = page

    def set(self, key, value):
        self.values[key] = value

    def getDictionary(self):
        return self.values

    def getAliases(self):
        return self.aliases

    def getDonations(self):
        return self.donations
