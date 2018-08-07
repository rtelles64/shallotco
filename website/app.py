#app.py: Definition of routes for web application Shallotco.com.
#__author__ = "Jenny, Mike, Patrick"

from flask import Flask, render_template, json, redirect, request,flash,url_for,send_file,session
from flaskext.mysql import MySQL
import os
import gc
from functools import wraps
from passlib.hash import sha256_crypt
from PIL import Image,ImageOps
import glob, os
import random
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


size = 500,500

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
    error = request.args.get('error')  # counterpart for url_for()
    imgCmd = "SELECT ThumbPath, ImageName, ImageId From ApprovedImg WHERE Views >= 350"
    category = "All"
    cursor.execute(imgCmd)
    conn.commit()
    data=cursor.fetchall()
    #render home page with the data that is being sent from DB
    return render_template("shallotHome.html",data=data,error=error,category=category)

#congradulation page
@app.route('/congratulations')
def congradulation():
    return render_template("congradulation.html")

#define search page
@app.route('/Search', methods=['POST', 'GET'])
def searchResult():
    error =''
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            _search = request.form['search']
            if request.form['category'] == '':
                _categoryName = "All"
            else:
                _categoryName = request.form['category']
            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            if (len(data) == 0):
                order = "SELECT ThumbPath, ImageName, Descr, ImageId FROM ApprovedImg WHERE ImageName Like %s OR Descr LIKE %s"
                cursor.execute(order,('%'+_search+'%','%'+_search+'%'))
                conn.commit()
            else:
                _categoryId=data[0][0]
                order = "SELECT ThumbPath, ImageName, Descr, ImageId FROM ApprovedImg WHERE CategoryId=%s and (ImageName Like %s OR Descr LIKE %s)"
                cursor.execute(order, (int(_categoryId), '%'+_search+'%','%'+_search+'%'))
                conn.commit()
            imgData=cursor.fetchall()
            imgCount=len(imgData)
            if(imgCount == 0):
                error = "We are sorry that the image you searched is not available, but here is our trending images for you:"
                return redirect(url_for('home',error=error))
            else:

                return render_template("ImageResult.html",imgData=imgData, imgCount=imgCount, search=_search, category=_categoryName)


        else:
            return redirect(url_for('home'))
    except Exception as e:
        return render_template("shallotHome.html",error = error)
    finally:
        cursor.close()
        conn.close()

#define searching for one particular image
@app.route('/Search/<string:imageid>', methods=['GET', 'POST'])
def imagePage(imageid):
    flash(imageid)
    conn = mysql.connect()
    cursor = conn.cursor()
    #select info from db for that imagename

    imgcmd = "SELECT FilePath, ImageName, Descr, UserId, Views FROM ApprovedImg WHERE ImageId = %s"
    cursor.execute(imgcmd, imageid)
    conn.commit()
    data = cursor.fetchall()
    flash(data)

    #get user name for displaying the image
    usernamecmd = "SELECT UserName FROM User WHERE IdUser = %s"
    cursor.execute(usernamecmd, data[0][3])
    conn.commit()
    userName=cursor.fetchall()
    userName=userName[0][0]

    #if user have clicked on this image, we will increase the view by 1
    view = "Update ApprovedImg set views=(%s) + 1 where ImageId = %s"
    cursor.execute(view, (data[0][4], imageid))
    conn.commit()
    return render_template("ImagePage.html", data=data,userName=userName)


def getUserId():
    #get user id with current user name
    conn = mysql.connect()
    cursor = conn.cursor()
    if 'UserName' in session:
        userName = session['UserName']
        order = "SELECT IdUser FROM User WHERE UserName = %s"
        cursor.execute(order,userName)
        conn.commit()
        data = cursor.fetchall()
        userId = data[0][0]
        return userId

#define upload image
@app.route('/UploadImage', methods = ['GET', 'POST'])
def uploadImage():
    imageCounter = random.randint(1,101)
    flash(imageCounter)
    flash("coming to uploadImage")
    #get user id for inserting image
    userId = getUserId()
    flash(userId)
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            #flash("coming to post")
            _descr = request.form['description']
            #flash("_descr")
            _categoryName = request.form['category']
            #flash("category")
            _imageName = request.form['imageName']
            #flash("_imageName")

            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            #data is a nested list, get category id from list
            _categoryId=data[0][0]
            flash(_categoryId)
            flash(APP_ROOT)
            #create the filepath that is going to store the images
            target = os.path.join(APP_ROOT, 'static/Images', _categoryName)
            flash(target)
            #loop through all the files that have been choosen by users
            for file in request.files.getlist("file"):
                filename = file.filename
                flash(filename)
                #create destination to save the file
                destination = "/".join([target, filename])
                flash(destination)
                file.save(destination)
                file, ext = os.path.splitext(filename)
                flash(file)
                flash(ext)
                im = Image.open(destination)
                im.thumbnail(size, Image.ANTIALIAS)
                thumbFullPath = os.path.join(APP_ROOT,'static/ThumbnailsImages', _categoryName)

                #create new file name to avoid the same file name from user
                filenameNew = file + str(imageCounter) + ext
                flash(filenameNew)
                fullpicPath = "/".join([target,filenameNew])
                #rename the file with the new file name
                if os.path.isfile(destination):
                    os.rename(destination, fullpicPath)
                thumbDestination = "/".join([thumbFullPath,filenameNew])
                flash("create thumbPath")
                flash(thumbDestination)
                if ext == '.jpg':
                    im.save(thumbDestination, 'jpeg')
                else:
                    flash("coming to else")
                    flash(filename.split('.')[-1])
                    im.save(thumbDestination, filename.split('.')[-1])
                #create the file path
                filePath = '/static/Images/' + _categoryName +'/' + filenameNew
                thumbPath = "/static/ThumbnailsImages/" + _categoryName + "/" + filenameNew
                flash(filePath)
                flash(thumbPath)
                order="INSERT INTO PendingImg (UserId,ImageName,Descr,CategoryId,FilePath,ThumbPath) VALUES (%s,%s,%s,%s,%s,%s)"
                value=((userId,_imageName,_descr,_categoryId,filePath,thumbPath))
                cursor.execute(order,value)
                flash("going to execute")
                conn.commit()
                flash("commit")
            #return to upload image page if users want to upload more
            message = "Thank you for uploading your image, now you can upload more images"
            return render_template("UploadImage.html", message=message)
        #if there is no post, simply return to upload image page
        return render_template("UploadImage.html")
    except Exception as e:
        error = 'Sorry, we are not able to upload your image'
        return render_template("UploadImage.html",error = error)
    finally:
        #flash("Closing DB conn")
        cursor.close()
        conn.close()

@app.route('/Admin')
def adminPage():
    conn = mysql.connect()
    cursor = conn.cursor()
    error = request.args.get('error')
    #_imageID = request.form['imageid']
    approvedCmd = "SELECT * FROM ApprovedImg"
    cursor.execute(approvedCmd)
    conn.commit()
    approvedData = cursor.fetchall()
    pendingCmd = "SELECT * FROM PendingImg"
    cursor.execute(pendingCmd)
    conn.commit()
    pendingData = cursor.fetchall()
    userCmd = "SELECT * FROM User WHERE IdUser > 1"
    cursor.execute(userCmd)
    conn.commit()
    userData = cursor.fetchall()
    #arg = [['aa', '111someone@gmail.com', '1/1/1/', 'azs', 'male', 'sj'], ['b', 'b111someone@gmail.com', '21/1/1/', 'bazs', 'fmale', 'nsj'], ['b', 'b111someone@gmail.com', '21/1/1/', 'bazs', 'fmale', 'nsj']]
    #arg2 = [['/static/Images/IMG_20170113_140535.jpg', 'a5zs'], ['/static/Images/IMG_20170113_140535.jpg', 'azs']]
    #arg3 = [['/static/Images/IMG_20170113_140535.jpg', 'a5zs'], ['/static/Images/IMG_20170113_140535.jpg', 'azs']]
    return render_template("/AdminPage.html", userData = userData, pendingData = pendingData, approvedData = approvedData)

@app.route('/Admin/Approve/<int:imageID>')
def adminApprove(imageID):
    conn = mysql.connect()
    cursor = conn.cursor()
    #_imageID = request.form['imageid']
    selectCmd = "SELECT UserId,ImageName,Descr,CategoryId,FilePath,ThumbPath FROM PendingImg WHERE ImageId = %s"
    cursor.execute(selectCmd, imageID)
    conn.commit()
    data = cursor.fetchall()
    moveCmd = "INSERT into ApprovedImg (UserId,ImageName,Descr,CategoryId,FilePath,ThumbPath) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(moveCmd, (data[0][0],data[0][1],data[0][2],data[0][3],data[0][4],data[0][5]))
    conn.commit()
    deleteCmd = "DELETE FROM PendingImg WHERE ImageId = %s"
    cursor.execute(deleteCmd, imageID)
    conn.commit()
    return redirect(url_for('adminPage'))

@app.route('/Admin/Delete/<string:table>/<int:imageID>')
def adminDelete(table, imageID):
    conn = mysql.connect()
    cursor = conn.cursor()
    #_imageID = request.form['imageid']
    if table == 'A':
        deleteCmd = "DELETE FROM ApprovedImg WHERE ImageId = %s"
        cursor.execute(deleteCmd, imageID)
        conn.commit()
        return redirect(url_for('adminPage'))
    if table == 'P':
        deleteCmd = "DELETE FROM PendingImg WHERE ImageId = %s"
        cursor.execute(deleteCmd, imageID)
        conn.commit()
        return redirect(url_for('adminPage'))
    if table == 'U':
        deleteCmd = "DELETE FROM User WHERE IdUser = %s"
        cursor.execute(deleteCmd, imageID)
        conn.commit()
        return redirect(url_for('adminPage'))

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
            #flash(_user)
            _password = sha256_crypt.encrypt(str(request.form['password']))
            #flash(_password)
            #passHash = sha256_crypt.encrypt(str(_password))
            #flash(passHash)
            _email = request.form['email']
            #flash(_email)
            _gender = request.form['gender']
            #flash(_gender)
            _city = request.form['city']
            #flash(_city)
            _country = request.form['country']
            #flash(_country)
            _firstName = request.form['firstName']
            #flash(_firstName)
            _lastName = request.form['lastName']
            #flash(_lastName)
            _day = request.form['day']
            _month = request.form['month']
            _year = request.form['year']
            _dob=_month +"/" + _day + "/" + _year

            flash(_dob)

            #insert new user to db if there is no error occur
            MYSQLCmd = "INSERT INTO User (UserName,Password,Email,Gender,Dob,City,Country,FirstName,LastName ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            #flash("writing command")
            cursor.execute(MYSQLCmd,(_user,_password,_email,_gender,_dob,_city,_country,_firstName,_lastName))
            #flash("finish execute")
            conn.commit()
            #flash("finish commit")
            #For collecting gabage
            gc.collect()
            #send confirmation message when the user has successfully registered
            flash("Thank you for signing up! Now you can log in")
            #return to homepage when user is successfully registered
            return redirect(url_for('login'))
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
            userCmd = "SELECT Password, IdUser FROM User WHERE UserName = %s"
            cursor.execute(userCmd, attempted_username)
            conn.commit()
            data = cursor.fetchall()
            #flash(data)
            flash(data[0][1])
            if sha256_crypt.verify(attempted_password,data[0][0]) == True:
                if data[0][1] == 1:
                    session['logged_in'] = True
                    session['UserName'] = attempted_username
                    return redirect(url_for('adminPage'))
                else:
                    session['logged_in'] = True
                    session['UserName'] = attempted_username
                    flash(session['UserName'])
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
