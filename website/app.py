from flask import Flask, render_template, json, request,flash,url_for,send_file
from flaskext.mysql import MySQL
import os

#import base64
mysql = MySQL()
app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

# MySQL configurations BACK END TEAM!!!!!!!!!!!!!!!!
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BackEnd2921'
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True
)

mysql.init_app(app)


@app.route('/')
def Home():
    # flash("in home page")
    conn = mysql.connect()
    cursor = conn.cursor()
    imgCmd = "SELECT filePath, ImageName From ApprovedImg WHERE Views >= 350"
    cursor.execute(imgCmd)
    conn.commit()
    data=cursor.fetchall()
    # flash(data)
    return render_template("shallotHome.html",data=data)

@app.route('/Search/<string:image>', methods=['GET', 'POST'])
def ImagePage(image):
    conn = mysql.connect()
    cursor = conn.cursor()
    imgcmd = "SELECT filePath, ImageName, Descr FROM ApprovedImg WHERE ImageName = %s"
    cursor.execute(imgcmd, image)
    conn.commit()
    data = cursor.fetchall()
    # flash(data)
    # if request.method == 'POST':
    #     return send_file(image, attachment_filename='testing.jpg', as_attachment=True)
    return render_template("ImagePage.html", data=data)

@app.route('/Upload')
def Upload():
    return render_template("UploadImage.html")

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route('/UploadImage', methods = ['GET', 'POST'])
def UploadImage():
    flash("coming to uploadImage")
    conn = mysql.connect()
    cur = conn.cursor()
    if request.method == 'POST':
        flash("coming to post")
        _descr = request.form['description']
        _categoryName = request.form['category']
        _imageName = request.form['imageName']
        categoryCmd = "SELECT IdCategory FROM Category WHERE CatgeoryName = %s"
        cursor.execute(categoryCmd,_categoryName)
        conn.commit()
        data=cursor.fetchall()
        _categoryId=data[0][0]
        flash(_categoryId)
        for file in request.files.getlist("file"):
            filename = file.filename
            flash(filename)
            filePath = "/static/Images/" + filename
            order="INSERT INTO Photo (userId,ImageName,Descr,categoryId,filePath) VALUES (%s,%s,%s,%s,%s)"
            value=((10,_imageName,_descr,_categoryId,filePath))
            cur.execute(order,value)
            conn.commit()



@app.route('/Search', methods=['POST', 'GET'])
def searchResult():
    error =''
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
    #flash(request.method)
        if request.method == 'POST':
            # flash("in post")
            _search = request.form['search']
            # flash(_search)
            _categoryName = request.form['category']
            # flash(_categoryName)
            categoryCmd = "SELECT IdCategory FROM Category WHERE CatgeoryName = %s"
            cursor.execute(categoryCmd,_categoryName)
            conn.commit()
            # flash("comeing to commit")
            data=cursor.fetchall()
            # flash(data)
            if (len(data) == 0):
                # flash("come if")
                order = "SELECT filePath, ImageName, Descr FROM ApprovedImg WHERE ImageName Like %s OR Descr LIKE %s"
                cursor.execute(order,('%'+_search+'%','%'+_search+'%'))
                conn.commit()
                # flash("come here if")
            else:
                _categoryId=data[0][0]
                # flash(_categoryId)
                # flash("come to else")
                order = "SELECT filePath, ImageName, Descr FROM ApprovedImg WHERE categoryId=%s and (ImageName Like %s OR Descr LIKE %s)"
                cursor.execute(order,(int(_categoryId), '%'+_search+'%','%'+_search+'%'))
                conn.commit()
                # flash("come here else")
            imgData=cursor.fetchall()
            # flash(imgData)
            if(len(imgData) == 0):
                flash("Sorry, the image is not available, but here is our trending images for you")
                return redirect(url_for('/'))
            else:
       		#flash("it has come to else")
                return render_template("ImageResult.html",imgData=imgData)
        else:
    	# flash("else")
            return redirect(url_for('/'))
    except Exception as e:
    #flash (e)
        return render_template("shallotHome.html",error = error)
    finally:
    #flash("Closing DB conn")
        cursor.close()
        conn.close()

@app.route('/About')
def about():
	return render_template("About.html")

@app.route('/Register')
def register():
    return render_template("register.html")

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
