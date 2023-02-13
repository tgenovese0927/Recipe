import requests
import passwords
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    class Recipe(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        description = db.Column(db.Text, nullable=False)
        img_url = db.Column(db.String(250), nullable=False)
        recipe_url = db.Column(db.String(250), nullable=False)

        def __repr__(self):
            return '<HtmlCode %r>' % self.code


    db.create_all()


class FindRecipeForm(FlaskForm):
    title = StringField("Search For Recipe", validators=[DataRequired()])
    submit = SubmitField("Find Recipe")


headers = {
    "X-RapidAPI-Key": f"{passwords.api_key}",
    "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
}


@app.route("/", methods=["GET", "POST"])
def home():
    form = FindRecipeForm()
    all_recipes = Recipe.query.all()
    if form.validate_on_submit():
        meal = form.title.data
        parameters = {
            "query": meal,
            "addRecipeInformation": True,
            "number": 10,
        }
        response = requests.request("GET", URL, headers=headers, params=parameters)

        data = response.json()["results"]
        return render_template("select.html", form=form, data=data)

    return render_template("index.html", form=form, recipes=all_recipes)


@app.route("/find", methods=["GET", "POST"])
def find_recipe():
    recipe_id = request.args.get("id")
    if recipe_id:
        find_url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{recipe_id}/information"
        response = requests.get(find_url, headers=headers)
        data = response.json()
        new_recipe = Recipe(
            title=data["title"],
            description=data["summary"],
            img_url=data["image"],
            recipe_url=data["sourceUrl"]
        )
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    recipe_id = Recipe.query.get_or_404(id)
    try:
        db.session.delete(recipe_id)
        db.session.commit()
        return redirect(url_for("home"))

    except:
        return "There was a problem deleting that"


if __name__ == '__main__':
    app.run(debug=True)
