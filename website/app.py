from flask import Flask, render_template, json, request,flash,url_for
from flaskext.mysql import MySQL

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
	return render_template("shallotHome.html")


@app.route('/Search', methods=['POST', 'GET'])
def searchResult():
	#flash("in search")
	error =''
	conn = mysql.connect()
	cursor = conn.cursor()
	try:
		#flash(request.method)
		if request.method == 'POST':
		#	flash("in post")
			_search = request.form['search']
		#	flash(_search)
			order = "SELECT filePath, ImageName, Descr FROM Image WHERE ImageName Like %s OR Descr LIKE %s"
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
				return render_template("ImageResult.html",data=data)
		else:
		#	flash("else")
			return redirect(url_for('/'))
	except Exception as e:
		#flash (e)
		return render_template("Prototype.html",error = error)
	finally:
		#flash("Closing DB conn")
		cursor.close()
		conn.close()
@app.route('/About')
def about():
	return render_template("About.html")

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
