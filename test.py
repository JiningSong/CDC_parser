
from requests_html import HTMLSession

session = HTMLSession()
r = session.get('https://pythonclock.org')
r.html.render()
print(r.html.html)