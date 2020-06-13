from flask import Flask, request, session, redirect, flash
from flask.templating import render_template
from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import yaml
import os

app = Flask(__name__)
Bootstrap(app)

db = yaml.load(open('db.yaml'))

app.config['MYSQL_HOST'] = db['Mysql_host']
app.config['MYSQL_USER'] = db['Mysql_user']
app.config['MYSQL_PASSWORD'] = db['Mysql_password']
app.config['MYSQL_DB'] = db['Mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

CKEditor(app)

app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/', methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM blog")
    if resultValue > 0:
        blogs = cur.fetchall()
        return render_template('index.html', blogs=blogs)
    cur.close()
    return render_template('index.html', blogs=None)

@app.route('/blogs/<int:id>/')
def blogs(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if resultValue > 0:
        blogs = cur.fetchone()
        return render_template('blogs.html', blogs=blogs)
    return 'Blog not found !!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['password'] != userDetails['confirm_password']:
            flash("both password must be same", 'danger')
            return render_template('register.html')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(first_name, last_name, email, username, password) VALUES(%s,%s,%s,%s,%s)", (userDetails['first_name'], userDetails['last_name'], userDetails['email'], userDetails['username'], generate_password_hash(userDetails['password'])))
        mysql.connection.commit()
        cur.close()
        flash('registration successful, please log into your account ', 'success')
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM user WHERE username = %s", ([username]))
        if resultValue > 0:
            user = cur.fetchone()
            if check_password_hash(user['password'], userDetails['password']):
                session['login'] = True
                session['firstName'] = user['first_name']
                session['lastName'] = user['last_name']
                flash('welcome' + ' ' + session['firstName'] + ' ' + '! you are successfully loged in','success')
            else:
                cur.close()
                flash('password does not match', 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('user not found !!!', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')

@app.route('/write-blog', methods=['GET', 'POST'])
def write_blog():
    if request.method == 'POST':
        userDetails = request.form
        title = userDetails['title']
        body = userDetails['body']
        author = session['firstName'] + ' ' + session['lastName']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blog(title,body,author) VALUES(%s,%s,%s)",(title, body, author))
        mysql.connection.commit()
        cur.close()
        flash('successfully blog regitered', 'success')
        return redirect('/')
    return render_template('write-blog.html')

@app.route('/edit-blog/<int:id>/', methods=['GET', 'POST'])
def edit_blog(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cur.execute("UPDATE blog SET title = %s,body = %s WHERE blog_id = %s",(title,body,id))
        mysql.connection.commit()
        flash('Edited successfully', 'success')
        return redirect('/blogs/{}'.format(id))
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if resultValue > 0:
        blog = cur.fetchone()
        return render_template('edit-blog.html',blog=blog)

@app.route('/my-blogs/')
def view_blogs():
    author = session['firstName'] + ' ' + session['lastName']
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM blog WHERE author = %s",[author])
    if result_value > 0:
        my_blogs = cur.fetchall()
        return render_template('my-blog.html',my_blogs=my_blogs)
    else:
        return render_template('my-blog.html',my_blogs=None)


#@app.route('/my-blog')
#def my_blog():
    #author = session['firstName'] + ' ' + session['lastName']
    #cur = mysql.connection.cursor()
    #resultValue = cur.execute(" SELECT * FROM blog WHERE author = %s", [author])
    #if resultValue > 0:
        #my_blogs = cur.fetchall()
        #return render_template('my-blog.html',my_blogs=my_blogs)
    #else:
        #return render_template('my-blog.html', my_blogs=None)


@app.route('/delete-blog/<int:id>/')
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blog WHERE blog_id={}".format(id))
    cur.connection.commit()
    flash('your blog has been deleted successfully', 'success')
    return redirect('/my-blogs')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/logout')
def logout():
    session.clear()
    flash('you are logged out', 'info')
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
