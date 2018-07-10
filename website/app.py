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

@app.route('/Search', methods=['POST', 'GET'])
def search():
    try:
        _search = request.form['search']

    # validate the received values
    if _search:


    #All Good, let's call MySQL
    ########################   BACK END TEAM   ######################################
    #If everything has gone right, the _search variable above should be holding the search value

    #Code from before, can use to help you get started
    #         conn = mysql.connect()
    #         cursor = conn.cursor()
    #         _hashed_password = generate_password_hash(_password)
    #         cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
    #         data = cursor.fetchall()
    #
    #         if len(data) is 0:
    #             conn.commit()
    #             return json.dumps({'message': 'User created successfully !'})
    #         else:
    #             return json.dumps({'error': str(data[0])})
    #     else:
    #         return json.dumps({'html': '<span>Enter the required fields</span>'})
    #
    # except Exception as e:
    #     return json.dumps({'error': str(e)})
    # finally:
    #     cursor.close()
    #     conn.close()


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
