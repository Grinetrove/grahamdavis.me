from flask import Flask, render_template
from BIS372_Delivery2 import bis372Blueprint

app = Flask(__name__)
app.register_blueprint(bis372Blueprint)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)