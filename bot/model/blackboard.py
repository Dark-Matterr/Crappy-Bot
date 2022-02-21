import mechanize
import bs4
import json

class Blackboard:
    def __init__(self, host, api, id='', passw=''):
        self.host = host
        self.api = api
        self.login(id, passw)


    def login(self, id, passw):
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.cookies = mechanize.CookieJar()
        self.browser.set_handle_refresh(False)
        self.browser.open(self.host)
        self.browser.select_form(nr=1)
        self.browser.form['user_id'] = id
        self.browser.form['password'] = passw
        self.browser.submit()

    def data(self, endpoint):
        response = self.browser.open(self.api + endpoint)
        parse = bs4.BeautifulSoup(response, "html.parser")
        load = json.loads(parse.text)
        return load
    
    def assignment(self, json):
        arr = dict()
        current_subject = ""
        item = []
        for x in range(0, len(json["results"])):
            if json["results"][x]["type"] == "GradebookColumn":
                if current_subject != json["results"][x]["calendarId"]:
                    current_subject = json["results"][x]["calendarId"]
                    item = []
            item.append(json["results"][x]["title"])
            item.append(json["results"][x]["end"])
            arr[current_subject] = item
            return arr
    
    def announcement(self, json):
        arr = dict()
        title = ""
        for x in range(0, len(json["results"])):
            title = json["results"][x]["title"]
            try:
                arr[str(json["results"][x]["created"])] = [title, str(json["results"][x]["body"])]
            except:
                arr[str(json["results"][x]["created"])] = [title, "-- The content is empty --"]
        return arr
        


