from sqlalchemy.orm import validates
from datetime import datetime, timedelta, timezone
from hashlib import md5
from app import app, db, login
import jwt

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean(), default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    topics = db.relationship('Topic', backref='user', lazy=True)
    replys = db.relationship('Reply', backref='user', lazy=True)
    about_me = db.Column(db.String(140))
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, followers.c.followed_id == Post.user_id
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
        except:
            return None
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<Post {self.body}>'


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(600))
    type = db.Column(db.String(50), nullable=False)
    course = db.relationship("Course", backref="subject", lazy=True)
    project = db.relationship("Project", backref="subject", lazy=True)
    article = db.relationship("Article", backref="subject", lazy=True)

    @validates('type')
    def validate_type(self, key, value):
        if value not in ['Language', 'Other']:
            raise ValueError('Invalid type')
        return value


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coursename = db.Column(db.String(200))
    description = db.Column(db.String(600))
    chapters = db.relationship('Chapter', backref='course', lazy=True)
    project = db.relationship('Project', backref='course')
    Path = db.Column(db.String(10), nullable=False)
    related_subj = db.Column(db.Integer, db.ForeignKey('subject.id'))

    @validates('Path')
    def validate_path(self, key, value):
        if value not in ['Career', 'Skill', 'None']:
            raise ValueError('Invalid path')
        return value


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'course.id'), nullable=False)
    lessons = db.relationship('Lesson', backref='chapter', lazy=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projectname = db.Column(db.String(200))
    description = db.Column(db.String(600))
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    related_subj = db.Column(db.Integer, db.ForeignKey('subject.id'))


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    related_subj = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship("Subject", backref="lesson", lazy=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey(
        'chapter.id'), nullable=False)

# new code
# ----------------------------------------------------------------------------
class ConceptTopic(db.Model):
    __tablename__ = 'concepttopic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(600))
    docs = db.relationship("Docs", backref="concepttopic")

class Docs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    desc = db.Column(db.String(1000))
    related_topic = db.Column(db.Integer, db.ForeignKey('concepttopic.id'))




class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    author = db.Column(db.String(100))
    description = db.Column(db.String(6000))
    related_subj = db.Column(db.Integer, db.ForeignKey('subject.id'))
    

# ---------------------------- LAU HING PUI START FROM HERE ---------------------------- #


class ForumCat(db.Model):
    __tablename__ = 'forumcats'
    id = db.Column(db.Integer, primary_key=True)
    forumcatsname = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(400))
    color = db.Column(db.String(6))
    is_deleted = db.Column(db.Boolean, default=False)
    topics = db.relationship('Topic', backref='forumcats', lazy=True)
    tags = db.relationship('ForumTag', backref='forumcats', lazy=True)


topic_tag = db.Table('topic_tag',
                     db.Column('topic_id', db.Integer,
                               db.ForeignKey('topics.id')),
                     db.Column('forumtags_id', db.Integer,
                               db.ForeignKey('forumtags.id'))
                     )

reply_like = db.Table('reply_like',
                      db.Column('reply_id', db.Integer,
                                db.ForeignKey('replys.id')),
                      db.Column('user_id', db.Integer,
                                db.ForeignKey('user.id'))
                      )


class ForumTag(db.Model):
    __tablename__ = 'forumtags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    forumcat_id = db.Column(db.Integer, db.ForeignKey(
        'forumcats.id'), nullable=False)


class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    forumcat_id = db.Column(db.Integer, db.ForeignKey(
        'forumcats.id'), nullable=False)
    title = db.Column(db.String(50))
    date = db.Column(db.Date, default=datetime.utcnow)
    votenum = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    replys = db.relationship('Reply', backref='topics')
    tags = db.relationship('ForumTag', secondary=topic_tag, backref='topics')

    @staticmethod
    def create_topic(author_id, forumcat_id, title, content, tagname):
        topic = Topic(
            author_id=author_id,
            forumcat_id=forumcat_id,
            title=title
        )
        db.session.add(topic)
        db.session.commit()

        reply_first = Reply.create_reply(content, topic.id, author_id, 0)
        db.session.add(reply_first)

        tags = tagname.split("#")
        tagsappend = []
        for tag in tags:
            if len(tag) < 1:
                continue
            tag_exist = db.session.query(ForumTag).filter_by(name=tag).first()

            if tag_exist == None:
                tagsappend.append(
                    ForumTag(
                        name=tag,
                        forumcat_id=forumcat_id
                    )
                )
            else:
                topic.tags.append(tag_exist)
                db.session.add(tag)
        for tag in tagsappend:
            topic.tags.append(tag)
            db.session.add(tag)
        db.session.commit()


class Reply(db.Model):
    __tablename__ = 'replys'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey(
        'topics.id'), nullable=False)
    content = db.Column(db.String(10000))
    is_reported = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    likers = db.relationship('User', secondary='reply_like',
                             backref=db.backref('likers', lazy='dynamic'))
    likenum = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('replys.id'))
    replys = db.relationship(
        'Reply', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')

    @staticmethod
    def create_reply(content, topic_id, author_id, parent_id):
        reply = Reply(
            content=content,
            topic_id=topic_id,
            author_id=author_id,
            parent_id=None if parent_id == 0 else parent_id
        )
        db.session.add(reply)
        db.session.commit()
        return reply
