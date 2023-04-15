#Use this file to add data in the database for courses for testing.
from app import db
from app.models import Subject, Course, Chapter, Project, Lesson


s1 = Subject(id= 1, name='Python', )
s2 = Subject(id=2, name='')
db.session.add(s1)
db.session.add(s2)
c1 = Course(id= 1,)
ch1 = Chapter(id= 1,)
p1 = Project()
l1 = Lesson()




db.session.commit()
