# Use this file to add data in the database for courses for testing.
from app import db,app
from app.models import Subject, Course, Chapter, Project, Lesson

app_context = app.app_context()
app_context.push()


s1 = Subject(id=1, name='Python',
             description='Python is a general-purpose, versatile, and powerful programming language.', type='Language')
s2 = Subject(id=2, name='HTML/CSS',
             description='HTML is the foundation of all web pages. It defines the structure of a page, while CSS defines its style',
             type='Language')
s3 = Subject(id=3, name='AI',
             description='Artificial intelligence (AI) uses computers and other machines to accomplish complicated tasks typically associated with the human mind — like problem-solving and decision-making.',
             type='Other')
s4 = Subject(id=4, name='Web Development',
             description='Web Development is the practice of developing websites and web apps that live on the internet.',
             type='Other')
db.session.add(s1)
db.session.add(s2)
db.session.add(s3)
db.session.add(s4)
c1 = Course(id=1, coursename='Learn Python 3',
            description='Learn the basics of Python 3.',related_subj =1, Path = 'None')
c2 = Course(id=2, coursename='Front-End Engineer',
            description='Learn the basics of Python 3.', related_subj =2, Path = 'Career')
c3 = Course(id=3, coursename='Machine Learning and AI Fundamentals',
            description='Machine Learning/AI Engineering is at the forefront of some of the most exciting technologies being developed today.', related_subj =3, Path = 'Skill')
db.session.add(c1)
db.session.add(c2)
db.session.add(c3)
ch1 = Chapter(id=1, title='Hello World', course_id=1)
db.session.add(ch1)
p1 = Project(id=1, projectname='Block Letters',
            description='Display your initials on the screen in block letters and create an ASCII art.',courseid = 1, related_subj=1)
db.session.add(p1)
l1 = Lesson(id=1, name='Hello World', related_subj=1, chapter_id=1)
db.session.add(l1)


db.session.commit()
