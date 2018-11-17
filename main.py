from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog", methods=['GET', 'POST'])
def index():
    id = request.args.get("id")

    if not id:
        listings = Blog.query.order_by(Blog.id.desc()).all()
        
        return render_template("blog.html", title="Build a Blog", listings=listings)
    else:
        listing = Blog.query.filter_by(id=id).first()
        name = listing.title
        body = listing.body
        
        return render_template("display_entry.html", name=name, body=body)

@app.route("/newpost", methods=["POST"])
def postform():
    name = request.form["name"]
    body = request.form["body"]

    title_error = ""
    body_error = ""

    if name == "":
        title_error = "Please enter a title"
    if body == "":
        body_error = "Please enter a post"

    if not title_error and not body_error:
        new_listing = Blog(name, body)
        db.session.add(new_listing)
        db.session.commit()
        id = new_listing.id

        return redirect("/blog?id=" + str(id))

    else:
        return render_template("newpost.html", title="Add a Blog", title_error=title_error, body_error=body_error, name=name, body=body)

@app.route("/newpost", methods=['GET'])
def getform():
    return render_template("newpost.html", title="Add a Blog")

if __name__ == "__main__":
    app.run()
