from app import db,app
from app.models import ConceptTopic, Docs

app_context = app.app_context()
app_context.push()
db.drop_all()
db.create_all()

ct1 = ConceptTopic(id=1, name='AI', description='E')
d1 = Docs(id=1, title='ChatGPT', desc='Chat', related_topic=1)

ct1.docs.append(d1)



db.session.add(ct1)
db.session.add(d1)
db.session.commit()