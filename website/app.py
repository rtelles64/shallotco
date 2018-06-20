from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


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
