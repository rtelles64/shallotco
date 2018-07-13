
from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BackEnd2921'
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)


def read_file(filename):
    with open(filename, 'rb') as f:
        photo = f.read()
    return photo


@app.route('/')
def users():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('''INSERT INTO User (Username,password,email) values('test1','password','email goes here' )''')
    data = cur.fetchall()
    print len(data)
    conn.commit()
def BLOB():
    conn = mysql.connect()
    cur = conn.cursor()
    data = read_file('IMG_20170113_140535.jpg')
    x='''INSERT INTO Photo (IdUser,PhotoName,Descr,IdCategory,IsPublic,Views,FullPic,Thumb) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
    y=((10,'photo name','description',1,1,1,data,data))
    cur.execute(x,y)
    conn.commit()
     
def BLOBRET():
    conn = mysql.connect()
    cur = conn.cursor()
    x="SELECT FullPic FROM Photo WHERE IdPhoto = %s"
    y=5
    cur.execute(x, (y,))
    conn.commit()
    photo = cur.fetchone()[0]
    write_file(photo, 'retrieved2.jpeg')
    write_file(photo,'test.txt')

if __name__ == '__main__':
     BLOB()
     BLOBRET()
