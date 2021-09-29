from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import requests
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///10_movies_db.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api_key = "sdlfkjsdlfjsdkfjsdkfjsldfjlsfj"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

class EditForm(FlaskForm):
    rating = StringField("Your rating out of 10 e.g. 8.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddmForm(FlaskForm):
    title = StringField("Name of the movie", validators=[DataRequired()])
    submit = SubmitField("Done")


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, autoincrement=True)
    ranking = db.Column(db.String(10))
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))


db.create_all()


def search_film(title):
    and_point = "https://api.themoviedb.org/3/search/movie"
    api_key = "5a56a6e23122bdfd207b4d7915a0dce3"
    header = {
        "api_key": api_key,
        "query": title
    }
    response = requests.get(and_point, params=header).json()
    film_data = response['results']
    return film_data


@app.route("/")
def home():
    all_films = Movies.query.order_by(Movies.rating).all()

    for i in range(len(all_films)):
        all_films[i].ranking = len(all_films) - i
        db.session.commit()
    return render_template("index.html", all_movies=all_films)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    film_id = request.args.get('id')
    movie = Movies.query.get(film_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = AddmForm()
    if add_form.validate_on_submit():
        film_name = add_form.title.data
        film_data = search_film(film_name)
        return render_template("select.html", data=film_data)

    return render_template('add.html', form=add_form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    film_id = request.args.get('id')
    film_to_delete = Movies.query.get(film_id)
    db.session.delete(film_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/select", methods=["GET", "POST"])
def select():
    select_film = ast.literal_eval(request.args.get('select_film'))
    print(select_film)
    new_film = Movies(
        title=select_film["original_title"],
        year=select_film['release_date'],
        description=select_film['overview'],
        rating=0,
        ranking=None,
        review=None,
        img_url=f"{MOVIE_DB_IMAGE_URL}{select_film['poster_path']}"
    )
    db.session.add(new_film)
    db.session.commit()
    film = Movies.query.filter_by(title=select_film["original_title"]).first()
    film_id = film.id
    return redirect(url_for('edit', id=film_id))


if __name__ == '__main__':
    app.run(debug=True)
