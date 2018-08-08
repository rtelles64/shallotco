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
def congratulation():
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
    #flash(imageid)
    conn = mysql.connect()
    cursor = conn.cursor()
    #select info from db for that imagename

    imgcmd = "SELECT FilePath, ImageName, Descr, UserId, Views FROM ApprovedImg WHERE ImageId = %s"
    cursor.execute(imgcmd, imageid)
    conn.commit()
    data = cursor.fetchall()
    #flash(data)

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
    #flash(imageCounter)
    #flash("coming to uploadImage")
    #get user id for inserting image
    userId = getUserId()
    #flash(userId)
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            _descr = request.form['description']
            _categoryName = request.form['category']
            _imageName = request.form['imageName']

            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            #data is a nested list, get category id from list
            _categoryId=data[0][0]
            #create the filepath that is going to store the images
            target = os.path.join(APP_ROOT, 'static/Images', _categoryName)
            #loop through all the files that have been choosen by users
            for file in request.files.getlist("file"):
                filename = file.filename
                if filename == '':
                    error_ = 'You must choose an image to upload'
                    return render_template("UploadImage.html",error=error_)
                else:
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
                        #flash("coming to else")
                        #flash(filename.split('.')[-1])
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
                return render_template("uploadConfirm.html", message=message)
        #if there is no post, simply return to upload image page
        return render_template("UploadImage.html")
    except Exception as e:
        error = 'Sorry, we are not able to upload your image'
        return render_template("UploadImage.html",error = error)
    finally:
        #Close DB connection
        cursor.close()
        conn.close()

#Route for Admin capabilities
@app.route('/Admin')
def adminPage():
    #Open DB connection
    conn = mysql.connect()
    cursor = conn.cursor()
    error = request.args.get('error')
    #Get the current user's User Id
    userId = getUserId()
    #Check to see if the Admin is currently logged in
    if userId == 1:
        #_imageID = request.form['imageid']
        #Select everything in the ApprovedImg table
        approvedCmd = "SELECT * FROM ApprovedImg"
        cursor.execute(approvedCmd)
        conn.commit()
        #Store all info from ApprovedImg in the approvedData array
        approvedData = cursor.fetchall()
        #Select everything in the PendingImg table
        pendingCmd = "SELECT * FROM PendingImg"
        cursor.execute(pendingCmd)
        conn.commit()
        #Store all info from PendingImg in the pendingData array
        pendingData = cursor.fetchall()
        #Select everything in the User table
        userCmd = "SELECT * FROM User WHERE IdUser > 1"
        cursor.execute(userCmd)
        conn.commit()
        #Store all info from User in the userData array
        userData = cursor.fetchall()
        #Render the Admin page and pass along all pertinent info
        return render_template("/AdminPage.html", userData = userData, pendingData = pendingData, approvedData = approvedData)
    else:
        #If the Admin is not logged in, redirect back to the home page
        return redirect(url_for('home',error=error))

#Route for approving a certain image as Admin
@app.route('/Admin/Approve/<int:imageID>')
#Define a function and pass to it the image ID of the selected image
def adminApprove(imageID):
    #Open database connection
    conn = mysql.connect()
    cursor = conn.cursor()
    #_imageID = request.form['imageid']
    #SQL command for selecting info from the PendingImg table
    selectCmd = "SELECT UserId,ImageName,Descr,CategoryId,FilePath,ThumbPath FROM PendingImg WHERE ImageId = %s"
    cursor.execute(selectCmd, imageID)
    conn.commit()
    #Storing data from the SQL select in the data array
    data = cursor.fetchall()
    #SQL command for inserting info into ApprovedImg from the data array
    moveCmd = "INSERT into ApprovedImg (UserId,ImageName,Descr,CategoryId,FilePath,ThumbPath) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(moveCmd, (data[0][0],data[0][1],data[0][2],data[0][3],data[0][4],data[0][5]))
    conn.commit()
    #SQL command to delete the inserted image from the PendingImg table
    deleteCmd = "DELETE FROM PendingImg WHERE ImageId = %s"
    cursor.execute(deleteCmd, imageID)
    conn.commit()
    #Return to the original admin page and re-load the tables
    return redirect(url_for('adminPage'))

#Route for deleting a certain image as Admin
@app.route('/Admin/Delete/<string:table>/<int:imageID>')
#Define a function and pass to it the image ID and table of the selected image
def adminDelete(table, imageID):
    #Open database connection
    conn = mysql.connect()
    cursor = conn.cursor()
    #_imageID = request.form['imageid']
    #If statements specifying which table to delete from
    if table == 'A':
        #SQL command to delete from ApprovedImg table
        deleteCmd = "DELETE FROM ApprovedImg WHERE ImageId = %s"
        cursor.execute(deleteCmd, imageID)
        conn.commit()
        #Redirect back to original Admin route
        return redirect(url_for('adminPage'))
    if table == 'P':
        #SQL command to delete from PendingImg table
        deleteCmd = "DELETE FROM PendingImg WHERE ImageId = %s"
        cursor.execute(deleteCmd, imageID)
        conn.commit()
        #Redirect back to original Admin route
        return redirect(url_for('adminPage'))
    if table == 'U':
        #SQL command to delete from User table
        deleteCmd = "DELETE FROM User WHERE IdUser = %s"
        cursor.execute(deleteCmd, imageID)
        conn.commit()
        #Redirect back to original Admin route
        return redirect(url_for('adminPage'))

#Route for the entire About page
@app.route('/About')
def about():
	return render_template("About.html")

#Route for registration page
@app.route('/Register', methods=["GET","POST"])
def register():
    error =''
    #Open database connection
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            #Collecting all information from front end form
            _user = request.form['userName']
            #Encrypt the entered password with sha256 and store in a variable
            _password = sha256_crypt.encrypt(str(request.form['password']))
            _email = request.form['email']
            _gender = request.form['gender']
            _city = request.form['city']
            _country = request.form['country']
            _firstName = request.form['firstName']
            _lastName = request.form['lastName']
            _day = request.form['day']
            _month = request.form['month']
            _year = request.form['year']
            #Set up DOB in proper format
            _dob=_month +"/" + _day + "/" + _year
            #Insert new user into database if there is no error occurring
            MYSQLCmd = "INSERT INTO User (UserName,Password,Email,Gender,Dob,City,Country,FirstName,LastName ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(MYSQLCmd,(_user,_password,_email,_gender,_dob,_city,_country,_firstName,_lastName))
            conn.commit()
            #For collecting garbage
            gc.collect()
            #Send confirmation message when the user has successfully registered
            flash("Thank you for signing up! Now you can log in")
            #Return to homepage when user is successfully registered
            return redirect(url_for('login'))
        #If there is no post, render register page
        return render_template("register.html")
    except Exception as e:
        #If there is an exception thrown, send error message and redirect to the register page
        error="sorry, an error has occured when register, please try again"
        return render_template("register.html", error=error)
    finally:
        cursor.close()
        conn.close()

#Definition for login check function
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap

#Route for logging in
@app.route('/Login', methods=["GET","POST"])
def login():
    error = ''
    #Open database connection
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if request.method == "POST":
            #Pull username/password data from front end form
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            #SQL command to select information from User table with supplied username
            userCmd = "SELECT Password, IdUser FROM User WHERE UserName = %s"
            cursor.execute(userCmd, attempted_username)
            conn.commit()
            #Input selected information into the data array
            data = cursor.fetchall()
            #Check to see if the supplied password matches the encrypted password
            if sha256_crypt.verify(attempted_password,data[0][0]) == True:
                #Check to see if the user is an Admin, redirect to admin page
                if data[0][1] == 1:
                    session['logged_in'] = True
                    session['UserName'] = attempted_username
                    return redirect(url_for('adminPage'))
                #If the user is not Admin, redirect to home page
                else:
                    session['logged_in'] = True
                    session['UserName'] = attempted_username
                    return redirect(url_for('home'))
            else:
                #Error has occured when logging in
                error = "Invalid credentials. Try Again."
        #Garbage collection
        gc.collect()
        #Return to login page with error
        return render_template("Login.html", error = error)
    except Exception as e:
        #If exception was thrown, reload login page with error
        error = "Login failed, please try again"
        return render_template("Login.html", error = error)

#Route for logging out of user's account
@app.route('/Logout')
@login_required
def logout():
    #Clear the session of any user data
    session.clear()
    flash("You have been logged out!")
    #Garbage collection
    gc.collect()
    #Return to home screen
    return redirect(url_for('home'))

#Route for Roy about page
@app.route('/About/Roy')
def Roy():
	return render_template("About/RoyTelles.html")

#Route for Jenny about page
@app.route('/About/Jenny')
def Jenny():
	return render_template("About/DandanCai.html")

#Route for James about page
@app.route('/About/James')
def James():
	return render_template("About/James.html")

#Route for Mike about page
@app.route('/About/Michael')
def Michael():
	return render_template("About/Michael.html")

#Route for Patrick about page
@app.route('/About/Patrick')
def Patrick():
	return render_template("About/Patrick.html")

#Route for Sam about page
@app.route('/About/Sam')
def Sam():
	return render_template("About/sam.html")


if __name__ == '__main__':
	app.run(debug=True)
