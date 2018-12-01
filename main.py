from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:Mendoza@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'DebMendoza'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    #Constructor
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    #Constructor
    def __init__(self, username, password):
        self.username = username
        self.password = password

#fxn from get-it-done
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#fxn from user-signup
@app.route("/login", methods=['POST', 'GET'])
def login():

    name_error = ""
    pw_error = ""
      
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('newpost')
        if not user:
            name_error = "Username does not exist"
        if user and user.password != password:
            pw_error = "Password is incorrect"
             
    return render_template("login.html", name_error=name_error, pw_error=pw_error)

#fxn from get-it-done/ user-signup
@app.route("/signup", methods=['POST', 'GET'])
def signup():

    name_error = ""
    pw_error = ""
    ver_pw_error = ""
    username = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #Verify username
        if username == "":
            name_error = "Please enter username"

        if len(username) < 3 or len(username) > 20:
            name_error = "Username must be between 3 and 20 characters"
    
        for char in username:
            if char == " ":
                name_error = "No spaces allowed"
            else:
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    name_error = "Username is unavailable"
                    username = ""

        #Verify password
        if password == "":
            pw_error = "Please enter password"
    
        if len(password) < 3 or len(password) > 20:
            pw_error = "Password must be between 3 and 20 characters"
            password = ""

        if " " in password:
            pw_error = "No spaces in password"
            password = ""

        #Verify verify-password
        if verify != password:
            ver_pw_error = "Passwords do not match"

        if not name_error and not pw_error and not ver_pw_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template("signup.html", name_error=name_error, pw_error=pw_error, ver_pw_error=ver_pw_error, username=username)

#fxn from build-a-blog
@app.route("/blog", methods=['GET', 'POST'])
def blog():

    id = request.args.get("id")
    user_id = request.args.get("user")

    if not id and not user_id:
        listings = Blog.query.order_by(Blog.id.desc()).all()
        
        return render_template("blog.html", title="Blogz", listings=listings)
    
    if not user_id:
        listing = Blog.query.filter_by(id=id).first()
        owner_id = listing.owner_id
        name = listing.title
        body = listing.body
        username = listing.owner.username
        return render_template("display_entry.html", name=name, body=body, username=username, owner_id=owner_id, listing=listing)
    else:
        owner = User.query.filter_by(id=user_id).first()
        listings = Blog.query.filter_by(owner=owner).order_by(Blog.id.desc()).all()
        
        return render_template("blog.html", title=owner.username, listings=listings, user=user_id)

#fxn from get-it-done
@app.route("/logout")
def logout():
    del session['username']
    return redirect('/index')

#fxn from build-a-blog
@app.route("/newpost", methods=["POST"])
def postform():

    owner = User.query.filter_by(username=session['username']).first()

    name = request.form["name"]
    body = request.form["body"]

    title_error = ""
    body_error = ""

    if name == "":
        title_error = "Please enter a title"
    if body == "":
        body_error = "Please enter a post"
    
    if not title_error and not body_error:
        new_listing = Blog(name, body, owner)
        db.session.add(new_listing)
        db.session.commit()
        id = new_listing.id

        return redirect("/blog?id=" + str(id))

    else:
        return render_template("newpost.html", title="Add Blog Entry", title_error=title_error, body_error=body_error, name=name, body=body)

#fxn from build-a-blog
@app.route("/newpost", methods=['GET'])
def getform():
    return render_template("newpost.html", title="Add Blog Entry")

@app.route('/index', methods=['GET'])
def index():
    user_list = User.query.all()
    return render_template('index.html', title="Bloggers", user_list=user_list)

if __name__ == "__main__":
    app.run()
