import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# the documentation
# https://documenter.getpostman.com/view/18914730/UVRDHmKm
##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # converting the column to dictionary so we can use them in the serialization JSON
    # convert SQLAlchemy Column object to a Python dict
    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)

        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


# here we will create an api request that allow developer to get access to random Cafe
@app.route("/random", methods=["GET"])
def get_random_cafe():
    # we method to get random cafes from Db
    # all_cafe = []
    # all_data = db.session.query(Cafe).all()
    # for cafe_name in all_data:
    #     all_cafe.append(cafe_name.name)
    # c = random.choice(all_cafe)
    # ---------------------------------------------------------------------------------------

    # get a random cafe from the db attribute
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)

    # Now we want to put the data in JSON we called this serialization
    # this is one way but the problem is when we add new column to the db we have to manually add it here

    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })
    # ___________________________________________________________________________________
    # لو سوينا له الامر اللي تحت بدون استدعاء فانكشن تو دكشنري بيكون الداتا تحتوي على دكشنري واحد فقط
    # return jsonify(cafe=random_cafe.name)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.

    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all_cafe", methods=["GET"])
def all_cafe():
    cafes = db.session.query(Cafe).all()

    # ---------------------------------------------------------------------------
    # solution with regular list
    all_cafes = []
    for cafe in cafes:
        all_cafes.append(cafe.to_dict())
    return jsonify(cafe=all_cafes)

    # _____________________________________________________________________________
    # This uses a List Comprehension but you could also split it into 3 lines.
    # return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


# ________________________________________________________________________________

# solution without using cafe.to_dict() function
# cafe_list = []
# for cafe in cafes:
#     cafe_dict = {"id": cafe.id, "name": cafe.name, "map_url": cafe.map_url,
#                  "img_url": cafe.img_url,
#                  "location": cafe.location, "has_sockets": cafe.has_sockets,
#                  "has_toilet": cafe.has_toilet, "has_wifi": cafe.has_wifi,
#                  "can_take_calls": cafe.can_take_calls, "seats": cafe.seats,
#                  "coffee_price": cafe.coffee_price}
#     cafe_list.append(cafe_dict)
# all_cafes = {"cafes": cafe_list}
# all_cafes_json = jsonify(cafes=all_cafes["cafes"])
# return all_cafes_json


@app.route("/search", methods=['GET'])
def search():
    # this is the api link and it showing how to make request
    # 127.0.0.1:5000/search?loc=peckham
    # loc = the word we put in the url to check location
    # if loc in the link
    if "loc" in request.args:
        # get the value of the loc
        location = request.args["loc"].capitalize()
        all_cafes = Cafe.query.filter_by(location=location).all()

        # If the name provided by the user is not in the db then do this
        # if the name is not in db in this case the len of all_cafes is 0
        if len(all_cafes) == 0:
            return {"Error": {
                "Not found": "Sorry, we don't have a cafe at that location."
            }}
        else:
            data = []
            for cafe in all_cafes:
                data.append(cafe.to_dict())
            return jsonify(cafes=data)

        # عشان لو دخل الرابط غلط يطلع له هالرساله ولا يطلع له غلط

    else:
        return {"Error": {
            "No field": "No location field provided. Please specify the location."
        }}


# this websirte help us build the api
# https://web.postman.co/workspace


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# ------------------------------------------------------------------------------

# Updating data via API

# PUT vs PATCH in HTTP
# PUT = updating the entire entry to the db
# PATCH = you only sending the piece of data that need to be updated like for ex location

@app.route("/update-price/<int:cafe_id>", methods=["PATCH", "GET"])
def patch_new_price(cafe_id):
    if "new_price" in request.args:

        new_price = request.args.get("new_price")
        cafe = db.session.query(Cafe).get(cafe_id)
        # now we updating the db and committing the update
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})

    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        # if the cafe exist in the db
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        # if the cafe doesn't exist
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

        # if the api wrong
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
