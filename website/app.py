#app.py: Definition of routes for web application Shallotco.com.
#__author__ = "Jenny, Mike, Patrick"

from flask import Flask, render_template, json, redirect, request,flash,url_for,send_file,session
from flaskext.mysql import MySQL
import os
import gc
from functools import wraps
from passlib.hash import sha256_crypt

mysql = MySQL()
app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

#Configure DB to allow to connect to DB
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BackEnd2921'
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True
)

mysql.init_app(app)

#define home page
@app.route('/')
def home():
    #create db connection
    conn = mysql.connect()
    cursor = conn.cursor()
    imgCmd = "SELECT FilePath, ImageName From ApprovedImg WHERE Views >= 350"
    cursor.execute(imgCmd)
    conn.commit()
    data=cursor.fetchall()
    #render home page with the data that is being sent from DB
    return render_template("shallotHome.html",data=data)

#define search page
@app.route('/Search', methods=['POST', 'GET'])
def searchResult():
    error =''
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            _search = request.form['search']
            _categoryName = request.form['category']
            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            if (len(data) == 0):
                order = "SELECT FilePath, ImageName, Descr FROM ApprovedImg WHERE ImageName Like %s OR Descr LIKE %s"
                cursor.execute(order,('%'+_search+'%','%'+_search+'%'))
                conn.commit()
            else:
                _categoryId=data[0][0]
                order = "SELECT FilePath, ImageName, Descr FROM ApprovedImg WHERE CategoryId=%s and (ImageName Like %s OR Descr LIKE %s)"
                cursor.execute(order, (int(_categoryId), '%'+_search+'%','%'+_search+'%'))
                conn.commit()
            imgData=cursor.fetchall()
            imgCount=len(imgData)
            if(imgCount == 0):
                error = "Sorry, the image is not available, but here is our trending images for you:"
                return redirect(url_for('home'))
            else:
                return render_template("ImageResult.html",imgData=imgData, error=error, imgCount=imgCount, search=_search)
        else:
            return redirect(url_for('home'))
    except Exception as e:
        return render_template("shallotHome.html",error = error)
    finally:
        cursor.close()
        conn.close()

#define searching for one particular image
@app.route('/Search/<string:image>', methods=['GET', 'POST'])
def imagePage(image):
    conn = mysql.connect()
    cursor = conn.cursor()
    imgcmd = "SELECT FilePath, ImageName, Descr FROM ApprovedImg WHERE ImageName = %s"
    cursor.execute(imgcmd, image)
    conn.commit()
    data = cursor.fetchall()
    return render_template("ImagePage.html", data=data)

#define upload image
@app.route('/UploadImage', methods = ['GET', 'POST'])
def uploadImage():
    flash("coming to uploadImage")
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            flash("coming to post")
            _descr = request.form['description']
            flash("_descr")
            _categoryName = request.form['category']
            flash("category")
            _imageName = request.form['imageName']
            flash("_imageName")
            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            #data is a nested list, get category id from list
            _categoryId=data[0][0]
            flash(_categoryId)
            #loop through all the files that have been choosen by users
            for file in request.files.getlist("file"):
                filename = file.filename
                flash(filename)
                #create the file path
                filePath = "/static/Images/" + filename
                order="INSERT INTO PendingImg (UserId,ImageName,Descr,IdCategory,FilePath) VALUES (%s,%s,%s,%s,%s)"
                value=((10,_imageName,_descr,_categoryId,filePath))
                cursor.execute(order,value)
                # if int(x) > 0:
                #     error = "Sorry, we are not able to upload your image, please try again."
                #     return render_template("UploadImage.html", error=error)
                conn.commit()
            #return to upload image page if users want to upload more
            return render_template("UploadImage.html")
        #if there is no post, simply return to upload image page
        return render_template("UploadImage.html")
    except Exception as e:
        error = 'Sorry, we are not able to upload your image'
        return render_template("UploadImage.html",error = error)
    finally:
        #flash("Closing DB conn")
        cursor.close()
        conn.close()

@app.route('/admin')
def adminPage():
    arg = [['aa', '111someone@gmail.com', '1/1/1/', 'azs', 'male', 'sj'], ['b', 'b111someone@gmail.com', '21/1/1/', 'bazs', 'fmale', 'nsj']]
    arg2 = [['/static/Images/IMG_20170113_140535.jpg', '25zs'], ['/static/Images/IMG_20170113_140535.jpg', 'azs']]
    arg3 = [['/static/Images/IMG_20170113_140535.jpg', '25zs'], ['/static/Images/IMG_20170113_140535.jpg', 'azs']]
    return render_template("/AdminPage.html", userData = arg, pendingData = arg2, approvedData = arg3)

@app.route('/About')
def about():
	return render_template("About.html")

#define register page
@app.route('/Register', methods=["GET","POST"])
def register():
    error =''
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            #get all the fields value
            _user = request.form['userName']
            flash(_user)
            _password = sha256_crypt.encrypt(str(request.form['password']))
            flash(_password)
            #passHash = sha256_crypt.encrypt(str(_password))
            #flash(passHash)
            _email = request.form['email']
            flash(_email)
            _gender = request.form['gender']
            flash(_gender)
            _city = request.form['city']
            flash(_city)
            _country = request.form['country']
            flash(_country)
            _firstName = request.form['firstName']
            flash(_firstName)
            _lastName = request.form['lastName']
            flash(_lastName)
            _day = request.form['day']
            _month = request.form['month']
            _year = request.form['year']
            _dob=_month +"/" + _day + "/" + _year
            flash(_dob)
            #check if user name has existed in the DB
            # x = cursor.execute("SELECT * FROM USER WHERE UserName = %s",(_user))
            # if int(x) > 0:
            #     error = 'This user name has existed, please choose a different username!'
            #     #simple return to register page if error occurs
            #     return render_template("register.html", error=error)
            #insert new user to db if there is no error occur
            MYSQLCmd = "INSERT INTO User (UserName,Password,Email,Gender,Dob,City,Country,FirstName,LastName ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            flash("writing command")
            cursor.execute(MYSQLCmd,(_user,_password,_email,_gender,_dob,_city,_country,_firstName,_lastName))
            flash("finish execute")
            conn.commit()
            flash("finish commit")
            gc.collect()
            session['logged_in'] = True 
            #return to homepage when user is successfully registered
            return redirect(url_for('home'))
        #if there is no post, render register page
        return render_template("register.html")
    except Exception as e:
        error="sorry, an error has occured when register, please try again"
        return render_template("register.html", error=error)
    finally:
        cursor.close()
        conn.close()
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap

@app.route('/Login', methods=["GET","POST"])
def login():
    error = ''
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            userCmd = "SELECT Password FROM User WHERE UserName = %s"
            cursor.execute(userCmd, attempted_username)
            conn.commit()
            data = cursor.fetchall()
            flash(data)
            flash(data[0][0])
            if sha256_crypt.verify(attempted_password,data[0][0]) == True:
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                #error has occured when login
                error = "Invalid credentials. Try Again."
        gc.collect()
        return render_template("Login.html", error = error)
    except Exception as e:
        error = "Login failed, please try again"
        return render_template("Login.html", error = error)

@app.route('/Logout')
@login_required
def logout():
    # session.pop('logged_in', None)
    # flash('You were logged out.')
    # return redirect(url_for('home'))
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('home'))

@app.route('/About/Roy')
def Roy():
	return render_template("About/RoyTelles.html")


@app.route('/About/Jenny')
def Jenny():
	return render_template("About/DandanCai.html")


@app.route('/About/James')
def James():
	return render_template("About/James.html")


@app.route('/About/Michael')
def Michael():
	return render_template("About/Michael.html")


@app.route('/About/Patrick')
def Patrick():
	return render_template("About/Patrick.html")


@app.route('/About/Sam')
def Sam():
	return render_template("About/sam.html")


if __name__ == '__main__':
	app.run(debug=True)
