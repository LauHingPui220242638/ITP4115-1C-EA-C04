from app import db, app
from app.models import ConceptTopic, Docs

app_context = app.app_context()
app_context.push()
db.drop_all()
db.create_all()

ct1 = ConceptTopic(id=1, name='AI', description='Artificial Intelligence (AI) refers to both the study of intelligent agents and the intelligent agents themselves. An “intelligent agent” is any device designed to achieve some goal, receive information from its environment as input, and output a response that maximizes the success of achieving said goal.')
ct2 = ConceptTopic(id=2, name='Javascript', description='JavaScript is a fun and flexible programming language. It’s one of the core technologies of web development and can be used on both the front-end and the back-end. While HTML and CSS are languages that give structure and colors to web pages, JavaScript makes them interactive and come alive.')
ct3 = ConceptTopic(id=3, name='HTML', description='HTML, short for HyperText Markup Language, is the foundation of all web pages. It was created by Tim Berners-Lee in 1993 to define the structure of a web page. Without it, you wouldn’t be able to organize text or add images or videos to your pages. HTML is the beginning of everything you need to know to make your first website.')
# ct4 = ConceptTopic(id=3, name='Cloud Computing', description='Cloud computing refers to an architecture where computing resources and hardware are maintained and managed remotely by an entity other than the user. This is becoming popular with businesses and ubiquitous in personal computing. For example, whenever a person sets up a website on GoDaddy, plays World of Warcraft, or streams a movie on Netflix, they are using a cloud computing solution.')

db.session.add(ct1)
db.session.add(ct2)
db.session.add(ct3)
# db.session.add(ct4)


d1 = Docs(id=1, title='ChatGPT', desc='Chat', related_topic=1)

ct1.docs.append(d1)


db.session.add(d1)
db.session.commit()
