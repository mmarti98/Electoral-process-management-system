from applications.configuration import Configuration;
from flask import Flask, request, jsonify, Response;
from applications.models import database;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt;
from adminDecorator import roleCheck;
import csv;
import io;
from applications.daemon.application import checkVote;

application = Flask (__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);

@application.route("/", methods=["GET"])
def test_image():
    return "VotingStation image working";


@application.route ( "/vote", methods = ["POST"] )
@roleCheck(role ="user")
@jwt_required()
def vote ( ):
    if ("file" not in request.files):
        return jsonify(message="Field file is missing."), 400
    if (request.files["file"].filename == ""):
        return jsonify(message="Field file is missing."), 400

    content = request.files["file"].stream.read ( ).decode ( "utf-8" );
    stream = io.StringIO ( content);
    #csv podaci razdvojeni zarezom
    reader = csv.reader ( stream );
    linija = 0; #numeracija linija krece od 0
    #row je lista => guid,pollNumber
    for row in reader:
        if (len(row) != 2):
            return jsonify(message="Incorrect number of values on line {}.".format(linija)), 400
        guid = str(row[0]);
        pollString = row[1];
        try:
            pollNumber = int(pollString);
        except:
            return jsonify(message="Incorrect poll number on line {}.".format(linija)), 400
        if (0 > pollNumber):
            return jsonify(message="Incorrect poll number on line {}.".format(linija)), 400
        claims = get_jwt();
        checkVote(guid, pollNumber, claims["jmbg"]);
        linija = linija + 1;
    return Response(),200;


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True,host="0.0.0.0", port=5004);
