from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required

from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, AddSubjectForm, AddCourseForm, AddChapterForm, AddLessonForm
from app.models import User, Course, Subject, Post, Chapter, Lesson, Project, ConceptTopic, Docs, Article
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    courses = Course.query.filter(Course.Path == 'None')
    return render_template('index.html.j2', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, courses=courses)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html.j2', title=_('Register'), form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('user.html.j2', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title=_('Edit Profile'),
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))


#New code
@app.route('/projects')
def Projects():
    subject = Subject.query.all()
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    projects = Project.query.all()
    return render_template('projects.html.j2', title=_('Projects'), subject=subject,
     language=language, other=other, projects=projects)


@app.route('/projects/<int:id>')
def Projects_subj(id):
    subject = Subject.query.get(id)
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    projects = Project.query.filter(Project.related_subj == id)
    return render_template('projects_subj.html.j2', subject=subject, language=language, other=other, projects=projects)
#new codes
@app.route('/admin')
@login_required
def Admin():
    if current_user.is_admin == False:
        return redirect(url_for('index'))
    return render_template('admin.html.j2', title=_('Admin Options'))

@app.route('/admin/Subjects', methods=['GET', 'POST'])
@login_required
def Add_Subjects():
        if current_user.is_admin == False:
            return redirect(url_for('index'))
        form = AddSubjectForm()
        if form.validate_on_submit():
            last_subject = Subject.query.order_by(Subject.id.desc()).first()
            subject = Subject(id=last_subject.id + 1,
                               name=form.name.data, description=form.desc.data, type=form.type.data)
            db.session.add(subject)
            db.session.commit()
            flash(_('Subject Added.'))
            return redirect(url_for('Add_Subjects'))
        return render_template('ad_option.html.j2', title=_('Add Subject'), form=form)


@app.route('/admin/Courses', methods=['GET', 'POST'])
@login_required
def Add_Courses():
        if current_user.is_admin == False:
            return redirect(url_for('index'))
        form = AddCourseForm()
        if form.validate_on_submit():
            last_course = Course.query.order_by(Course.id.desc()).first()
            course = Course(id=last_course.id + 1,
                               coursename=form.name.data, description=form.desc.data,
                                 Path=form.path.data, related_subj=form.related_subj.data)
            db.session.add(course)
            db.session.commit()
            flash(_('Course Added.'))
            return redirect(url_for('Add_Courses'))
        return render_template('ad_option.html.j2', title=_('Add Course'), form=form)


@app.route('/admin/Chapters', methods=['GET', 'POST'])
@login_required
def Add_Chapters():
        if current_user.is_admin == False:
            return redirect(url_for('index'))
        form = AddChapterForm()
        if form.validate_on_submit():
            last_chapter = Chapter.query.order_by(Chapter.id.desc()).first()
            chapter = Chapter(id=last_chapter.id + 1, title=form.title.data, course_id=form.course_id.data)
            db.session.add(chapter)
            db.session.commit()
            flash(_('Chapter Added.'))
            return redirect(url_for('Add_Chapters'))
        
        return render_template('ad_option.html.j2', title=_('Add Chapter'), form=form)


@app.route('/admin/Lessons', methods=['GET', 'POST'])
@login_required
def Add_Lessons():
        if current_user.is_admin == False:
            return redirect(url_for('index'))
        form = AddLessonForm()
        if form.validate_on_submit():
            last_lesson = Lesson.query.order_by(Lesson.id.desc()).first()
            lesson = Lesson(id=last_lesson.id + 1, name=form.name.data, 
                            related_subj=form.related_subj.data, chapter_id=form.chapter_id.data)
            db.session.add(lesson)
            db.session.commit()
            flash(_('Lesson Added.'))
            return redirect(url_for('Add_Lessons'))
        
        return render_template('ad_option.html.j2', title=_('Add Chapter'), form=form)


@app.route('/catalog')
def catalog():
    subject = Subject.query.all()
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    career = Course.query.filter(Course.Path == 'Career')
    courses = Course.query.filter(Course.Path == 'None')
    return render_template('catalog.html.j2', title=_('Catalog'), subject=subject, career=career,
                           language=language,other=other, courses=courses)


@app.route('/catalog/all')
def catalog_cour():
    subject = Subject.query.all()
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    career = Course.query.filter(Course.Path == 'Career')
    skills = Course.query.filter(Course.Path == 'Skill')
    courses = Course.query.filter(Course.Path == 'None')
    return render_template('catalog_cour.html.j2', title=_('Full Catalog'), subject=subject, career=career, skills=skills,
                           language=language,other=other, courses=courses)


@app.route('/catalog/<int:id>')
def catalog_subj(id):
    subject = Subject.query.get(id)
    courses = Course.query.filter(Course.related_subj == id)
    return render_template('catalog_subj.html.j2', title=_(subject.name), subject=subject, courses=courses)


@app.route('/course/<int:id>')
def course(id):
    course = Course.query.get(id)
    if not course:
        return redirect(url_for('index'))
    return render_template('course.html.j2', title=_(course.coursename), course=course)


@app.route('/docs')
def docs():
    topics = ConceptTopic.query.all()
    docs = Docs.query.all()
    return render_template('docs.html.j2', title=_('Docs'), topics=topics, docs=docs)


@app.route('/docs/<int:id>')
def doc_topic(id):
    topics = ConceptTopic.query.all()
    cur_topic = ConceptTopic.query.get(id)
    related_doc = Docs.query.filter(Docs.related_topic == id)
    return render_template('docs_topic.html.j2', title=_(cur_topic.name),cur_topic=cur_topic, topics=topics, related_doc=related_doc)

@app.route('/docs/concept/<int:id>')
def doc_content(id):
    topics = ConceptTopic.query.all()
    concept = Docs.query.get(id)
    
    return render_template('doc_cont.html.j2', title=_(concept.title), topics=topics, concept=concept)

@app.route('/articles')
def articles():
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    articles = Article.query.all()
    return render_template('article_list.html.j2', title=_('Articles'), language=language,other=other,articles=articles)

@app.route('/articles/subject/<int:id>')
def article_subj(id):
    subject = Subject.query.get(id)
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    articles = Article.query.filter(Article.related_subj == id)
    return render_template('articles_sub.html.j2', title=_('Areticles'),subject=subject, language=language, articles=articles, 
                           other=other)


@app.route('/articles/<int:id>')
def article_content(id):
    language = Subject.query.filter(Subject.type == 'Language')
    other = Subject.query.filter(Subject.type == 'Other')
    article = Article.query.get(id)
    return render_template('article_cont.html.j2', title=_(article.name), language=language, other=other, article=article)