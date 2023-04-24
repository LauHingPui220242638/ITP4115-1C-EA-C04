from flask import render_template,url_for, redirect, Blueprint, request, make_response
from sqlalchemy import desc
from random import random
from app import app, db
from app.models import User, ForumCat, ForumTag, Topic, Reply 
from flask_login import login_user, logout_user, current_user, login_required
from .forum_forms import ReplyForm,EditReplyForm, TopicForm
forum = Blueprint('forum',__name__,url_prefix="/forum")

@forum.route("/")
def home():
    forumcats = db.session.query(ForumCat).all()
    return render_template('forum_home.html.j2', forumcats=forumcats)




@forum.route("/forumcats/<id>")
def forumcats(id):
    forumcat = ForumCat.query.get(id)
    form = TopicForm()
    topics = forumcat.topics
    for topic in topics:
        topic.author = User.query.get(topic.author_id).username
        topic.likecount = 0
        for reply in topic.replys:
            topic.likecount += reply.likenum
    
    return render_template('forum_topic_by_cat.html.j2', forumcat=forumcat, topics=topics, form=form )



@forum.route("/forumcats/<id>",  methods = ["POST"])
@login_required
def forumcats_topic(id):
    forumcat = ForumCat.query.get(id)
    form = TopicForm()
    if form.is_submitted():
        Topic.create_topic(
            int(current_user.id),
            int(forumcat.id),
            form.title.data,
            form.content.data,
            form.tagname.data
            )
    return redirect(request.referrer)





@forum.route("/topic_last/")
def topic_last():
    topic_id = request.cookies.get("topic_last")
    if topic_id != None:
        return redirect(url_for("forum.topic", id=topic_id))
    else:
        return redirect("forum")

@forum.route("/topic/<id>", methods=["GET"])
def topic(id):
    topic = Topic.query.get(id)
    form = ReplyForm()
    forumcat = ForumCat.query.get(topic.forumcat_id)
    replys = db.session.query(Reply).filter_by(topic_id= id).order_by(desc(Reply.date)).all()
    for reply in replys:
        reply.author = User.query.get(reply.author_id).username
        likers = reply.likers
        reply.likecount = len(likers)
        reply.likable = False if current_user in likers else True
    render = render_template('forum_reply_by_topic.html.j2', topic=topic, replys=replys, forumcat=forumcat, form=form )
    resp = make_response(render)
    resp.set_cookie("topic_last",value=id,max_age=1000)
    return resp



@forum.route("/topic/<id>",  methods = ["POST"])
@login_required
def topic_reply(id):
    topic = Topic.query.get(id)
    form = ReplyForm()
    if form.is_submitted():
        Reply.create_reply(
            form.content.data,
            topic.id,
            current_user.id,
            form.parent_id.data
            )
    return redirect(request.referrer)


@forum.route("/admin",methods = ["GET"])
@login_required
def admin():
    if current_user.is_admin == True:
        replys =  Reply.query.all()
        replys_list = []
        reply_count = 0
        for reply in replys:
            if reply.is_reported == True and reply.is_deleted == False:
                form = EditReplyForm()
                reply_count +=1
                reply.author = User.query.get(reply.author_id).username
                form.content.data = reply.content
                reply.form = form
                replys_list.append(reply)

        return render_template('forum_reply_by_admin.html.j2', replys=replys_list, reply_count=reply_count)
    else:
        return redirect('404')

@forum.route("/admin",  methods = ["POST"])
@login_required
def admin_unreport():
    form = EditReplyForm()
    if form.is_submitted():
        reply_id = form.reply_active.data
        reply = Reply.query.get(reply_id)
        reply.is_reported = False
        
        reply.content = form.content.data
        
        db.session.commit()
        return redirect(request.referrer)
    else:
        return redirect('404')

    
    


@forum.route("/report_reply")
@login_required
def report_reply():
    
    reply_id = request.args.get('reply_id')
    reply = Reply.query.get(reply_id)
    reply.is_reported = True
    
    db.session.commit()
    return ('', 204)

@forum.route("/delete_reply")
@login_required
def delete_reply():
    if current_user.is_admin == True:
        reply_id = request.args.get('reply_id')
        reply = Reply.query.get(reply_id)
        reply.is_deleted = True
            
        db.session.commit()
        return redirect(request.referrer)
    else:
        return render_template('404')
    
@forum.route("/like_reply")
@login_required
def like_reply():
    
    reply_id = request.args.get('reply_id')
    reply = Reply.query.get(reply_id)
    likers = reply.likers
    likable = False if current_user in likers else True
    if likable == True :
        reply.likenum += 1
        likers.append(current_user)
        db.session.commit()
        return redirect(request.referrer)
    else:
        reply.likenum -= 1
        likers.remove(current_user)
        db.session.commit()
        return redirect(request.referrer)



#For Debug Only
# @app.route("/create_forumcat/<catname>/<description>")
# def create_forumcat(catname,description):

#     forumcat = ForumCat(
#             color= "FF00FF",
#             forumcatsname = catname,
#             description = description
#         )
#     db.session.add(forumcat)
#     db.session.commit()
#     return forumcat.forumcatsname + "  " + forumcat.description


# @app.route("/create_forumtag/<tagname>")
# def create_forumtag(tagname):

#     forumtag = ForumTag(
#         name = tagname
#         )
#     db.session.add(forumtag)
#     db.session.commit()
#     return tagname + "ForumTag Create"



# @app.route("/find_tag/<tagname>")
# def find_tag(tagname):
#     tag = db.session.query(ForumTag).filter_by(name=tagname).first()
#     return str(tag.id)

# @app.route("/remove_tag/<tagname>/<post_id>")
# def remove_tag(tagname, post_id):
#     tag = db.session.query(ForumTag).filter_by(name=tagname).first()
#     post = db.session.query(Post).filter_by(id=post_id).first()
#     post.tags.remove(tag)
#     db.session.commit()
#     resp = f"{tag.name} is removed from{post.title}"
#     return resp

# @app.route("/add_tag_post/<postid>/<tagname>")
# def add_tag_post(postid,tagname):
#     tag = ForumTag(name=tagname)
#     post = db.session.query(Post).filter_by(id=postid).first()
#     post.tags.append(tag)
#     db.session.add(tag)

#     db.session.commit()
#     return tag.name + "  " + post.title


# @app.route("/find_tags_ofpost/<postid>")
# def find_tags_ofpost(postid):
#     post = db.session.query(Post).filter_by(id=postid).first()
#     resp = ''
#     for tag in post.tags:
#         resp += "  " + tag.name
#     return resp






# @app.route("/create_post/<title>/<content>/<tagname>/<author_id>/<forumcat_id>")
# def create_post(title,content,tagname,author_id,forumcat_id):
#     post = Post(
#         author_id = author_id,
#         forumcat_id = forumcat_id,
#         title = title
#     ) 
#     db.session.add(post)

    
#     reply_first = func_reply(content,post.id,author_id,0)
#     db.session.add(reply_first)
    
#     tags = tagname.split("_")
#     tagsappend = []
#     for tag in tags:
#         tagsappend.append(
#             ForumTag(name=tag)
#         )
#     for tag in tagsappend:
#         post.tags.append(tag)
#         db.session.add(tag)
#     db.session.commit()
#     return "  ".join((post.title, str(post.author_id), str(post.forumcat_id) ,str(tag.name for tag in post.tags))) 




# @app.route("/find_post/<postid>")
# def find_post(postid):
#     post = db.session.query(Post).filter_by(id=postid).first()
    
#     author = User.query.get(post.author_id)
#     forumcat = ForumCat.query.get(post.forumcat_id)
#     resp = f"""
# Title : {post.title}  </br>   
# ID : {post.id} </br>    
# Category : {forumcat.forumcatsname} </br>    
#     """
#     resp += "Tags : "
#     for tag in post.tags:
#         resp += " #" + tag.name
    
#     resp += "</br>"
    
        
#     for reply in post.replys:
#         if reply.is_deleted != True:
#             reply_author = User.query.get(reply.author_id)
#             resp += f"""
# Author : {reply_author.username} </br>    
# Reply Content : {reply.content}</br>
# RID : {reply.id} </br>
# Likes : {reply.likenum} | Date : {reply.date}</br>
#             """
#             if reply.replys.count() > 0:
#                 for reply_replys in reply.replys:
#                     resp += f"*** Its Replys : {reply_replys.content} ***</br>"
#             resp += "</br></br></br>"
    
#     return resp



# @app.route("/create_reply/<content>/<post_id>/<author_id>/<parent_id>")
# def create_reply(content,post_id, author_id, parent_id):
#     reply = func_reply(content,post_id, author_id, parent_id)
#     db.session.add(reply)
#     db.session.commit()
#     resp = reply.content
#     return resp


# @app.route("/edit_reply/<reply_id>/<content>")
# def edit_reply(reply_id, content):
#     reply = db.session.query(Reply).filter_by(id=reply_id).first() 
#     reply.content = content
#     db.session.commit()
#     resp = str(reply.id) + " edited to " + reply.content
#     return resp



# @app.route("/delete_reply/<reply_id>")
# def delete_reply(reply_id):
#     reply = db.session.query(Reply).filter_by(id=reply_id).first() 
#     reply.is_deleted = True
#     db.session.commit()
#     resp = reply.is_deleted
#     return "Deleted ? " + str(resp)