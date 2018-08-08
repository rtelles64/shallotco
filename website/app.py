#app.py: Definition of routes for web application Shallotco.com.
#__author__ = "Jenny, Mike, Patrick"

from flask import Flask, render_template, json, redirect, request,flash,url_for,send_file,session
from flaskext.mysql import MySQL #library for mysql commands
import os
import gc
from functools import wraps
from passlib.hash import sha256_crypt #hashing library
from PIL import Image,ImageOps #ibrary for thumbnails
import glob, os
import random
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


size = 500,500

mysql = MySQL()
app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

#Configure app config values to connect to database from app.py
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BackEnd2921'
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True
)

mysql.init_app(app)

#The following code will be executed when the user enters the home page
@app.route('/')
def home():
    #create db connection
    conn = mysql.connect()
    cursor = conn.cursor()
    error = request.args.get('error')  # counterpart for url_for()
    #select popular images that have more than 350 views
    imgCmd = "SELECT ThumbPath, ImageName, ImageId From ApprovedImg WHERE Views >= 350"
    category = "All"
    cursor.execute(imgCmd)
    conn.commit()
    data=cursor.fetchall()
    #render home page and display the most the popular images
    return render_template("shallotHome.html",data=data,error=error,category=category)

#congradulation page
@app.route('/congratulations')
def congratulation():
    return render_template("congradulation.html")

# Upload Congratulation Page
@app.route('/uploadConfirm')
def upConfirm():
    return render_template("uploadConfirm.html")

#The following code will be executed when the user searches for an image
#The following code retrieves picture information based on image name, image description, and category information provided by the user
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
            #select category id that is equal to the user selected category received through POST from the Front End
            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            #if no category is selected then images from all categories that match the user request are returned
            if (len(data) == 0):
                order = "SELECT ThumbPath, ImageName, Descr, ImageId FROM ApprovedImg WHERE ImageName Like %s OR Descr LIKE %s"
                cursor.execute(order,('%'+_search+'%','%'+_search+'%'))
                conn.commit()
            #if a category is selected then images matching the user search values from the user specified category are returned
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

#When a user clicked on an image result the following code is executed
#The following code displays the image information of the image, including the image name and description as well as displaying the full size image
@app.route('/Search/<string:imageid>', methods=['GET', 'POST'])
def imagePage(imageid):
    conn = mysql.connect()
    cursor = conn.cursor()
    #select the filepath, imagename, description, uploader id and number of view for the image with the user provided image name
    imgcmd = "SELECT FilePath, ImageName, Descr, UserId, Views FROM ApprovedImg WHERE ImageId = %s"
    cursor.execute(imgcmd, imageid)
    conn.commit()
    data = cursor.fetchall()

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

#The following code is executed when the user uploads an image
@app.route('/UploadImage', methods = ['GET', 'POST'])
def uploadImage():
    imageCounter = random.randint(1,101)
    #get id of user who is uploading the image
    userId = getUserId()
    #connect to the database
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            _descr = request.form['description']
            _categoryName = request.form['category']
            _imageName = request.form['imageName']
            #select the id of the category selected by the user
            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            #data is a nested list, access category id in list and assign it to _categoryId
            _categoryId=data[0][0]
            #create the filepath of the location of where the uploaded file will be stored
            target = os.path.join(APP_ROOT, 'static/Images', _categoryName)
            #loop through all the files to be uploaded
            for file in request.files.getlist("file"):
                filename = file.filename
                #create destination to save the file
                destination = "/".join([target, filename])
                file.save(destination)
                file, ext = os.path.splitext(filename)
                im = Image.open(destination)
                im.thumbnail(size, Image.ANTIALIAS)
                thumbFullPath = os.path.join(APP_ROOT,'static/ThumbnailsImages', _categoryName)

                #create new file name to avoid the same file name from user
                filenameNew = file + str(imageCounter) + ext
                fullpicPath = "/".join([target,filenameNew])
                #rename the file with the new file name
                if os.path.isfile(destination):
                    os.rename(destination, fullpicPath)
                thumbDestination = "/".join([thumbFullPath,filenameNew])
                if ext == '.jpg':
                    im.save(thumbDestination, 'jpeg')
                else:
                    im.save(thumbDestination, filename.split('.')[-1])
                #create the file path
                filePath = '/static/Images/' + _categoryName +'/' + filenameNew
                thumbPath = "/static/ThumbnailsImages/" + _categoryName + "/" + filenameNew
                order="INSERT INTO PendingImg (UserId,ImageName,Descr,CategoryId,FilePath,ThumbPath) VALUES (%s,%s,%s,%s,%s,%s)"
                value=((userId,_imageName,_descr,_categoryId,filePath,thumbPath))
                cursor.execute(order,value)
                conn.commit()
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
    userId = getUserId()
    if userId == 1:
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
    else:
        return redirect(url_for('home',error=error))

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

            #flash(_dob)

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
            #flash("Thank you for signing up! Now you can log in")
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
            #flash(data[0][1])
            if sha256_crypt.verify(attempted_password,data[0][0]) == True:
                if data[0][1] == 1:
                    session['logged_in'] = True
                    session['UserName'] = attempted_username
                    return redirect(url_for('adminPage'))
                else:
                    session['logged_in'] = True
                    session['UserName'] = attempted_username
                    #flash(session['UserName'])
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
