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
def home():
    flash("in home page")
    conn = mysql.connect()
    cursor = conn.cursor()
    imgCmd = "SELECT filePath, ImageName From ApprovedImg WHERE Views >= 250"
    cursor.execute(imgCmd)
    conn.commit()
    data=cursor.fetchall()
    flash(data)
    return render_template("shallotHome.html",data=data)

@app.route('/Search/<string:image>', methods=['GET', 'POST'])
def ImagePage(image):
    print(image)
    if request.method == 'POST':
        return send_file(image, attachment_filename='testing.jpg', as_attachment=True)
    return render_template("About/ImagePage.html", downloadImage=image)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
	if request.method == 'POST':
		c = request.form['comment']
		ca = request.form['category']
		print(c + ' ' + ca)

		target = os.path.join(APP_ROOT, 'static/Images/')
		print(target)

		if not os.path.isdir(target):
			os.mkdir(target)
			print("directory created")

		for file in request.files.getlist("file"):
			print(file)
			filename = file.filename
			print(filename)
			destination = "/".join([target, filename])
			print(destination)
			file.save(destination)

	return render_template("UploadImage.html")



@app.route('/Search', methods=['POST', 'GET'])
def searchResult():
    error =''
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
    #flash(request.method)
        if request.method == 'POST':
    #	flash("in post")
            _search = request.form['search']
        #	flash(_search)
            # order = "SELECT filePath, ImageName, Descr FROM Image WHERE ImageName Like %s OR Descr LIKE %s"
            _categoryName = request.form['category']
            categoryCmd = "SELECT IdCategory FROM Category WHERE CategoryName = '%s' "
            cursor.execute(categoryId,_categoryName)
            conn.commit()
            data=cursor.fetchall()
            _categoryId=data[0]
            order = "SELECT CategoryId, filePath, ImageName, Descr FROM ApprovedImg WHERE (categoryId='%d' and (ImageName Like '%s' OR Descr LIKE '%s')) or ('%d'=0 and (ImageName Like '%s' OR Descr LIKE '%s'))"

            cursor.execute(order,(_categoryId,'%'+_search+'%','%'+_search+'%',_categoryId,'%'+_search+'%','%'+_search+'%'))
        #	flash("after")
            conn.commit()
            imgData=cursor.fetchall()
        #	flash(data)
            if(len(data) == 0):
                flash("Sorry, the image is not available, but here is our trending images for you")
                return redirect(url_for('/'))
            else:
       		flash("it has come to else")
                return render_template("ImageResult.html",data=data)
        else:
    #	flash("else")
            return redirect(url_for('/'))
    except Exception as e:
    #flash (e)
        return render_template("shallotHome.html",error = error)
    finally:
    #flash("Closing DB conn")
        cursor.close()
        conn.close()
@app.route('/ImageInfo')
def imageInfo():
	error =''
	conn = mysql.connect()
	cursor = conn.cursor()
	try:
		#flash(request.method)
		if request.method == 'POST':
		#	flash("in post")
			_search = request.form['search']
		#	flash(_search)
			order = "SELECT filePath, ImageName, Descr FROM ApprovedImg WHERE ImageName Like %s OR Descr LIKE %s"
			#flash(order)
                       # arg='%' + _search + '%'
			cursor.execute(order,('%'+_search+'%','%'+_search+'%'))
		#	flash("after")
			conn.commit()
			data=cursor.fetchall()
		#	flash(data)
			if(len(data) == 0):
				return redirect(url_for('/'))
			else:
			#	flash("it has come to else")
  				  return render_template("ImagePage.html",data=data)
		else:
		#	flash("else")
			return redirect(url_for('/'))
	except Exception as e:
		flash (e)
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
