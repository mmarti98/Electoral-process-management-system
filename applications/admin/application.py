from applications.configuration import Configuration;
from flask import Flask, request, jsonify;
from applications.models import database, Participant, Election, InvalidVotes, Vote;
from flask_jwt_extended import JWTManager, jwt_required;
from adminDecorator import roleCheck;
from datetime import datetime;
from dateutil import parser;
application = Flask (__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);

@application.route("/", methods=["GET"])
def test_image():
    return "Admin image working";

def is_valid_iso8601(iso_string):
    try:
        parser.parse(iso_string);
        result = True;
    except Exception:
        result = False;
    return result;

def checkDateAndTime(start,end):
    if (not is_valid_iso8601(start)):
        print("start not valid")
        return False;
    elif (not is_valid_iso8601(end)):
        print("not valid end")
        return False;
    elif (start > end):
        print("start>end")
        return False;

    print
    elections_list = Election.query.all();
    for election in elections_list:
        current_start = election.start;
        current_end = election.end;
        print(current_start);
        print(current_end)
        if (current_start <= start <= current_end or current_start <= end <= current_end):
            print("preklapa se sa drugim izborom")
            return False;

    return True;

def checkParticipants(individual, participants):
    #provjeriti da li svi participants imaju isti individual flag
    for participant_id in participants:
        try:
            id = int(participant_id);
        except: return False;
        participant_object = Participant.query.filter(Participant.id == id).first()
        print(participant_object.individual);
        if ( (not participant_object) or participant_object.individual != individual):
            print("participants error")
            return False;
    return True;

def getResultsForIndividualElections(id,participants):
    results = []
    votes = Vote.query.filter(Vote.election == id).all();
    all_votes = len(votes);
    print("All votes=" + str(all_votes));
    if (all_votes == 0):
        for i in range(0, len(participants)): results[i]=0;
        return results;
    for i in range(1, len(participants)+1):
        pollNumberVotes = Vote.query.filter(Vote.election == id).filter(Vote.pollNumber == i).all();
        pollNumberVotesCount = len(pollNumberVotes);
        print("pollNumber="+ str(pollNumberVotesCount));
        results.append(str(round(pollNumberVotesCount/all_votes, 2)))
    return results;

def getResultsForParliamentaryElections(id,participants):
    results = [];
    print(len(participants))
    for i in range(0, len(participants)): results.append(0);

    votes = Vote.query.filter(Vote.election == id).all();
    all_votes = len(votes);
    print("All votes=" + str(all_votes));
    if (all_votes == 0):
        return results;
    num_votes = [];
    for i in range(1, len(participants) + 1):
        pollNumberVotes = Vote.query.filter(Vote.election == id).filter(Vote.pollNumber == i).all();
        pollNumberVotesCount = len(pollNumberVotes);
        print("pollNumber=" + str(pollNumberVotesCount));
        if (round(pollNumberVotesCount / all_votes, 2) >= 0.05): #cenzus
            num_votes.append(pollNumberVotesCount);
            print("cenzus")
        else: num_votes.append(0); #ne ulaze u izbor

   
    current_value = []
    for i in range(1, len(participants) + 1):
        current_value.append(0)
    print(current_value);

    for i in range(0,250):
        for j in range(1,len(participants)+1):
            current_value[j-1] = num_votes[j-1] / (results[j-1]+1)
        max_value = 0;
        pollNumber = 0;
        for k in range(0,len(current_value)):
            if(current_value[k]>max_value):
                max_value=current_value[k];
                pollNumber=k;
        #reset vrijednosti
        for i in range(1, len(participants) + 1):
            current_value[i - 1] = 0;
        results[pollNumber] = results[pollNumber] + 1;

    return results;

@application.route("/createParticipant", methods=["POST"])
@roleCheck(role ="admin")
@jwt_required()
def createParticipant():
    name = request.json.get("name", "");
    individual = request.json.get("individual", None);

    nameEmpty = len(name) == 0;
    message = "";
    if (nameEmpty):
        message="Field name is missing.";
    elif (individual == None):
        message="Field individual is missing.";

    if (message != ""):
        return jsonify(message = message),400

    participant = Participant(
        name = name,
        individual = individual
    );

    database.session.add(participant);
    database.session.commit();

    return jsonify(id = participant.id), 200

@application.route("/getParticipants", methods=["GET"])
@roleCheck(role ="admin")
@jwt_required()
def getParticipants():
    participants_list = Participant.query.all()

    if (participants_list):
        json_serializable_participant = [];
        for participant in participants_list:
            json_participant = participant.serialize();
            json_serializable_participant.append(json_participant);
        return jsonify(participants = json_serializable_participant), 200
    return jsonify(participants = "There are no participants"),400

@application.route("/createElection", methods=["POST"])
@roleCheck(role ="admin")
@jwt_required()
def createElection():
    start = request.json.get("start", ""); # u ISO 8601
    end = request.json.get("end", "");     # u ISO 8601
    individual = request.json.get("individual", None);
    participants = request.json.get("participants", "");

    startEmpty = len(start) == 0;
    endEmpty = len(end) == 0;
    participantsEmpty = len(participants) == 0;
    participants_string = str(participants);
    message = "";
    participants_list_empty = True;
    if (participants_string == "[]"): participants_list_empty = False;

    if (startEmpty):
        message = "Field start is missing.";
    elif (endEmpty):
        message = "Field end is missing.";
    elif (individual == None):
        message = "Field individual is missing.";
    elif (participantsEmpty and participants_list_empty):
        message = "Field participants is missing.";

    if (message != ""):
        return jsonify(message=message), 400

    if (not checkDateAndTime (start,end)):
        message = "Invalid date and time.";
    elif ( (not participants_list_empty) or (len (participants) < 2) or (not checkParticipants(individual, participants)) ):
        message = "Invalid participants.";

    if (message != ""):
        return jsonify(message=message), 400

    election = Election (
        start = start,
        end = end,
        individual = individual ,
        participants= participants_string
    );

    database.session.add(election);
    database.session.commit();

    participants_size = len ( participants );
    pollNumbers = [];
    for x in range(1,participants_size+1):
        pollNumbers.append(x);
    return jsonify( pollNumbers = pollNumbers), 200


@application.route("/getElections", methods=["GET"])
@roleCheck(role ="admin")
@jwt_required()
def getElections():
    electionList = Election.query.all()
    if (electionList):
        elections = [];
        for election in electionList:
            participants = [];
            txt = election.participants;

            x = txt.split("[")
            x = x[1].split("]")
            x = x[0].split(", ")

            for i in range( 0, len(x)):
                participant = Participant.query.filter(Participant.id == int(x[i])).first()
                prepared_participant = {
                    "id": participant.id,
                    "name": participant.name
                }
                participants.append(prepared_participant)

            prepared_election = {
                "id": election.id,
                "start": election.start,
                "end": election.end,
                "individual": election.individual,
                "participants": participants
            }
            elections.append(prepared_election);
        return jsonify(elections = elections), 200
    return jsonify(elections = "No elections"),400

@application.route("/getResults", methods=["GET"])
@roleCheck(role ="admin")
@jwt_required()
def getResults():
    message = "";
    id = request.args.get('id');
    if (not id): message = "Field id is missing."
    if (id == ""): message = "Field id is missing."
    if (message != ""): return jsonify(message = message),400
    election = Election.query.filter(Election.id == id).first();
    if (not election): message = "Election does not exist."
    if (message != ""): return jsonify(message = message),400
    today = datetime.now().isoformat();
    if (today < election.end): return jsonify(message = "Election is ongoing." ),400
    print(id);
    invalidVotes_list = InvalidVotes.query.filter (InvalidVotes.election == id).all();

    json_serializable = [];
    if (invalidVotes_list):
        for vote in invalidVotes_list:
            json_participant = vote.serialize();
            json_serializable.append(json_participant);
    participants = []
    txt = election.participants;
    x = txt.split("[")
    x = x[1].split("]")
    x = x[0].split(", ")
    result = [];
    if (election.individual == True):
        result = getResultsForIndividualElections(id,x);
    else:
        result = getResultsForParliamentaryElections(id,x);
    for i in range(1, len(x)+1):
        participant = Participant.query.filter(Participant.id == int(x[i-1])).first()
        prepared_participant = {
            "pollNumber": i,
            "name": participant.name,
            "result":result[i-1]
        }
        participants.append(prepared_participant)
    return jsonify(participants = participants, invalidVotes = json_serializable),200


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True,host="0.0.0.0", port=5003);