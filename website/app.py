from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/About')
def about():
    return render_template("About.html")

@app.route('/Roy')
def Roy():
    return render_template("RoyTelles.html")

@app.route('/Jenny')
def Jenny():
    return render_template("DandanCai.html")

@app.route('/James')
def James():
    return render_template("James.html")

@app.route('/Michael')
def Michael():
    return render_template("Michael.html")

@app.route('/Patrick')
def Patrick():
    return render_template("Patrick.html")

@app.route('/Sam')
def Sam():
    return render_template("sam.html")

if __name__ == '__main__':
    app.run()
