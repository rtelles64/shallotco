
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


def users():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('''INSERT INTO User (Username,password,email) values('test1','password','email goes here' )''')
    data = cur.fetchall()
   # print len(data)
    conn.commit()

def BLOBRET():
    conn = mysql.connect()
    cur = conn.cursor()
    x="SELECT * FROM User"
    cur.execute(x)
    conn.commit()
    photo = cur.fetchone()[0]
    print(photo)

def BLOB():
    conn = mysql.connect()
    cur = conn.cursor()
    photo = read_file('test.jpeg')
    x='''INSERT INTO Image (userId,ImageName,Descr,categoryId,isPublic,views,FullPic,Thumb,isFullSize,isThumbnail) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    y=((2921,'Test1','This is a test of a potential Blob fix.',2,1,3000,photo,'\0',1,0))
    cur.execute(x,y)
    conn.commit()

if __name__ == '__main__':
     BLOB()
