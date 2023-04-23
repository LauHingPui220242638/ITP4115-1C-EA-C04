from app import db, app
from app.models import User, ForumCat, ForumTag, Topic, Reply


app_context = app.app_context()
app_context.push()
db.drop_all()
db.create_all()

#Forum User
u1 = User(username='Ben', email='ben@example.com')
u2 = User(username='May', email='may@example.com')
u3 = User(username='Tim', email = 'time@code.com')
u4 = User(username='ForumAdmin', email = 'forumadmin@code.com')
u1.set_password("Ben")
u2.set_password("May")
u3.set_password('Time')
u4.set_password('ForumAdmin')
db.session.add_all([u1,u2,u3,u4])

#Forum Category
fc1 = ForumCat(color= "FF00FF",forumcatsname = "HQ Announcements", description = "Here is where you’ll find the latest updates from The Codecademy Team. We will announce things like new product features, curriculum releases, and even site outages.")
fc2 = ForumCat(color= "5500FF",forumcatsname = "Getting Started", description = "New to the Forums? Orient yourself, get the tools, and learn the rules that will help make these Forums a helpful resource on your learning journey.")
fc3 = ForumCat(color= "5F50F5",forumcatsname = "Get Help", description = "Ask questions, get help with an exercise, and chat about your Codecademy coursework here. Click in for language-specific topic pages.")


p1 = Topic(author_id=1, forumcat_id=1, title="If you could do anything",)
p2 = Topic(author_id=2, forumcat_id=1, title="Learn ChatGPT with Codecademy!",)
p3 = Topic(author_id=3, forumcat_id=1, title="Spread Sheet Logic",)
p4 = Topic(author_id=4, forumcat_id=1, title="Big announcement!",)




r1 = Reply.func_reply("""
Hey y’all!

In an exciting new milestone for Codecademy, I’m proud to share our first ever TV commercial, inspired by many of the stories your fellow learners have shared right here in the community.

Check it out!
YB
I hope this continues to inspire you to unlock your full potential and continue your learning journey. Keep up the amazing work!
""",1,1,0)

r2 = Reply.func_reply("""
Well done CodeCademy, TV Commercial is on fire!!
I am active subscriber since 2020, closing the gap to my first 100 certificates, a working father with two lovely kids, always eager to learn, Codecademy offers high quality courses that continuously getting new material with new ideas, concepts and techniques, adapting every day in a rapidly changing era of technology, there is no better way to stay in top shape with cutting edge knowledge, a solid solution with a variety of choices to pick and start your new daily habit that will transform you, in a better version of you. Here is my LinkedIn profile, connect with me to celebrate together my first topic, when I reach my first 100 certificates.!!! (at 91 and going up!!)
https://www.linkedin.com/in/ioannis-e-kommas-6a8004a6/ 32
""",1,2,0)

r3 = Reply.func_reply("""
So, if you want to have a career as a Web Programmer, you have to understand programming languages, at least you have to master the programming languages ​​that are often used.
""",1,3,2)

r4 = Reply.func_reply("""
:fire: Wow!
Great work Codecademy Team
""",1,1,2)


t1 = ForumTag(name="geek",forumcat_id=1)
t2 = ForumTag(name="code",forumcat_id=1)
t3 = ForumTag(name="remind",forumcat_id=1)
t4 = ForumTag(name="soon",forumcat_id=1)

p1.tags.append(t1)
p1.tags.append(t2)
p1.tags.append(t3)
p1.tags.append(t4)

db.session.add_all([
    fc1,fc2,fc3,
    p1,p2,p3,p4,
    r1,r2,r3,r4,
    t1,t2,t3,t4
])


db.session.commit()
