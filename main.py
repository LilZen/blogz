from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def index(): 
    

    completed_blogs = Blog.query.all()   
    return render_template('blog.html', title="Build a Blog", completed_blogs=completed_blogs)

@app.route('/page')
def blog_page():
    
    page_title=request.args.get('blog_title')
    page_body=request.args.get('blog_body')
    page=Blog(page_title,page_body)
    return render_template('page.html',page=page)


@app.route('/newpost', methods=['POST', 'GET'])
def submit_post():

    blog = Blog.query.all()

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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')
    
        else:
            return render_template('newpost.html', blog=blog, blog_body_error=blog_body_error, blog_title=blog_title, blog_title_error=blog_title_error)    

    else:
        return render_template('newpost.html', blog=blog)

if __name__ == '__main__':
    app.run()