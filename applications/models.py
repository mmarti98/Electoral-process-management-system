from flask_sqlalchemy import SQLAlchemy;
import json

database = SQLAlchemy();

class Participant ( database.Model ):
    __tablename__ = "participants";
    id = database.Column ( database.Integer, primary_key = True );
    name = database.Column ( database.String(256), nullable = False );
    individual = database.Column ( database.Boolean, nullable = False );

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.name, self.individual);

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "individual": self.individual
            }

class Election ( database.Model ):
    __tablename__ = "elections";
    id = database.Column ( database.Integer, primary_key = True );
    start= database.Column(database.String(256), nullable = False);
    end=database.Column(database.String(256), nullable = False);
    individual = database.Column ( database.Boolean, nullable = False );
    participants = database.Column(database.String(256), nullable = False);

    def __repr__ ( self ):
        return "({}, {}, {}, {}, {})".format ( self.id, self.start, self.end, self.individual, self.participants);

    # toJSON() serializer method will return the JSON representation of the Object. i.e., It will convert custom Python Object to JSON string
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def serialize(self):
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "individual": self.individual
            }

class Vote ( database.Model ):
    __tablename__ = "votes";
    ballotGuid = database.Column(database.String(36), primary_key = True );
    electionOfficialJmbg = database.Column(database.String(13), nullable = False);
    pollNumber = database.Column(database.Integer, nullable = False);
    election = database.Column(database.Integer, nullable = False);

class InvalidVotes ( database.Model ):
    __tablename__ = "invalidVotes";
    ballotGuid = database.Column(database.String(36), primary_key = True)
    electionOfficialJmbg = database.Column(database.String(13), nullable = False);
    pollNumber = database.Column(database.Integer, nullable = False);
    reason = database.Column(database.String(256), nullable = False)
    election = database.Column(database.Integer, nullable = False)

    def serialize(self):
        return {
            "electionOfficialJmbg": self.electionOfficialJmbg,
            "ballotGuid": self.ballotGuid,
            "pollNumber": self.pollNumber,
            "reason": self.reason
            }
