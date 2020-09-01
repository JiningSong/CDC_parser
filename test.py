
# from requests_html import HTMLSession

# session = HTMLSession()
# r = session.get('https://pythonclock.org')
# r.html.render()
# print(r.html.html)
import re

text = "aaa (11) 2 (33) (dfasf)"
print(re.sub('\(\d+[^)]+\)', '', text))
