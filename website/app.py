from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations BACK END TEAM!!!!!!!!!!!!!!!!
app.config['MYSQL_DATABASE_USER'] = 'jay'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jay'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def home():
    return render_template("Prototype.html")

def image_base64(item):
        image_64 = base64.encodestring(item)
        return image_64

@app.route('/')
def home():
        return render_template("Prototype.html")


@app.route('/Search', methods=['POST', 'GET'])
def searchResult():
        error =''
        try:
                #flash("Come to try block")
                if request.method == 'POST':
                        conn = mysql.connect()
                        cursor = conn.cursor()
                        _search = request.form['search']
                        order = "SELECT FullPic FROM Image WHERE ImageName Like '%%s%'"
                        cursor.execute(order, (_search))
                        conn.commit()
                        data=cursor.fetchall()
                        #flash(data)
                        if(len(data) == 0):
                                return redirect(url_for('/'))
                        else:
                                return render_template("PrototypeResult.html")
                        cursor.close()
                        conn.close()
        except Exception as e:
                #flash (e)
                return render_template("Prototype.html",error = error)
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
    app.run()
