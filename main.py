from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password    

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        #validate signin
        if user and user.password == password:
            session['username'] = username
            flash("You are now logged into your build-a-blog")
            return redirect ('/blog')
        else:
        #TODO - fix this so it works when incorrect sign in given
            return flash("Invalid password or username","error")
    else:
        return render_template('login.html')   

@app.route('/signup', methods=['POST','GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        if len(username) < 3 or len(username) > 15:
            username_error = 'Please enter a username between 3 and 15 characters'
            username= ''
        if username.count(' ') > 0:
            username_error ='Spaces not allowed in  username'
            username = ''     

        if len(password) < 7 or len(password) > 15:
            password_error = 'Please enter a password between 7 and 15 characters'
            password = ''

        if password.count(' ') > 0:
            password_error = 'Spaces not allowed in password'
            password = ''    

        if password != verify:
            verify_error = 'Passwords do not match'
            verify = ''     
        if not username_error and not password_error and not verify_error:

            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
            # TODO - user better response messaging
                return "<h1>Duplicate user</h1>"
        else:
            return render_template('signup.html', username=username, username_error=username_error, password=password, password_error=password_error, verify=verify, verify_error=verify_error)        
        
    return render_template('signup.html')


@app.route('/blog')
def blog(): 
    #goes to individual blog page
    blog_id = request.args.get('id') 
    completed_blogs = Blog.query.all()
    
    if 'id' in request.args: 
        myblog = Blog.query.filter_by(id=blog_id).first()
        return render_template ('blog.html', myblog=myblog, blog_id=blog_id)
    
    return render_template ('blog.html', completed_blogs=completed_blogs)

@app.route('/blogz')
def blogz():
    id = request.args.get('userId')
    completed_blogs = Blog.query.filter_by(owner_id=id).all()
    
    return render_template('blogz.html', title="Build a Blog", completed_blogs=completed_blogs)

@app.route('/singleuser')
def singleuser():
    #lists all of users blogs, link 'your blog'
    owner = User.query.filter_by(username=session['username']).first()
    user_blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('singleUser.html', user_blogs=user_blogs)

@app.route('/')
def index(): 

    #Main blog page with full list usernames
    completed_users = User.query.all()   
    return render_template('index.html', completed_users=completed_users)

@app.route('/newpost', methods=['POST', 'GET'])
def submit_post():
    owner = User.query.filter_by(username=session['username']).first()
    blog = Blog.query.all()
    #checks for blog title and blog body is filled out
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        blog_title_error = ""
        blog_body_error = ""

        if len(blog_title) <= 0:
            blog_title_error = "Please provide a title."
            blog_title= ""

        if len(blog_body) <= 0:
            blog_body_error = "Please write a blog."

        if not blog_title_error and not blog_body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/blog?id={0}'.format(new_blog.id))   
        else:
            return render_template('newpost.html', blog=blog, blog_body_error=blog_body_error, blog_title=blog_title, blog_title_error=blog_title_error)    

    else:
        return render_template('newpost.html', blog=blog)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run() 