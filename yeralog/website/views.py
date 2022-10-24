import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_from_directory, abort, \
    send_file
from flask_login import login_required, current_user
from .models import Post, User, Contact
from . import db
import shutil
from werkzeug.utils import secure_filename
import imghdr

origin = '/home/yernazar/PycharmProjects/pythonProject1/yeralog/'
target = '/home/yernazar/PycharmProjects/pythonProject1/yeralog/website/uploads/'

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        uploaded_file = request.files['file']

        if not uploaded_file:
            flash('Post cannot be empty', category='error')
        else:
            if uploaded_file.filename != '':
                uploaded_file.save(uploaded_file.filename)
                shutil.move(origin + uploaded_file.filename, target)
                new_path = os.path.join(target + uploaded_file.filename)
            post = Post(path=uploaded_file.filename, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)

@views.route('/<filename>')
def upload(filename):
    return send_file(target+filename)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route('/contact', methods=['GET', 'POST'])
@login_required
def get_contact():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        new_message = Contact(email=email, name=name, subject=subject, message=message)
        db.session.add(new_message)
        db.session.commit()
        flash('Your message is delivered!')
        return redirect(url_for('views.home'))
    else:
        return render_template("contact.html")
