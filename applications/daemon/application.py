from applications.configuration import Configuration;
from flask import Flask;
from applications.models import database, Election, Vote, InvalidVotes;
from flask_jwt_extended import JWTManager;
from celery import Celery;
from datetime import datetime;

application = Flask (__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);

client = Celery(application.name, broker=application.config['CELERY_BROKER_URL'])
client.conf.update(application.config)

@application.route("/", methods=["GET"])
def test_image():
    return "Daemon image working";

@client.task()
def checkVote(guid,pollNumber,jmbg):
    print(guid);
    print(pollNumber);
    print(jmbg);
    #da li postoje trenutno izbori koji su aktivni, ako ne postoji glas se ne ubacuje u InvalidVote!!!
    today = datetime.now().isoformat();
    elections_list = Election.query.all();
    for election in elections_list:
        current_start = election.start;
        current_end = election.end;
        if (current_start <= today <= current_end ):
            print("traju izbori")
            # da li je zabiljezen glas
            has_vote = Vote.query.filter(Vote.ballotGuid == guid).first();
            if (has_vote):
                reason1 = "Duplicate ballot."
                invalidList = InvalidVotes.query.filter(InvalidVotes.ballotGuid == guid).first();
                if (invalidList): return;#ako vec postoji isti glas kao duplikat
                else:
                    invalidVote = InvalidVotes(
                        election = election.id,
                        reason = reason1,
                        pollNumber = pollNumber,
                        ballotGuid = guid,
                        electionOfficialJmbg =jmbg
                    )

                    database.session.add(invalidVote);
                    database.session.commit();
                    print("dodato u invalid")
                    return;
            # da li na datim izborima postoji ucesnik ciji je redni broj zaokruzen
            txt = election.participants;
            x = txt.split("[")
            x = x[1].split("]")
            x = x[0].split(", ")
            if (len(x) < pollNumber ):
                reason2 = "Invalid poll number."
                invalidList = InvalidVotes.query.filter(InvalidVotes.ballotGuid == guid).first();
                if (invalidList): return;
                else:
                    invalidVote = InvalidVotes(
                        election=election.id,
                        reason=reason2,
                        pollNumber=pollNumber,
                        ballotGuid=guid,
                        electionOfficialJmbg=jmbg
                    )

                    database.session.add(invalidVote);
                    database.session.commit();
                    print("dodato u invalid")
                    return;

            vote = Vote(
                election=election.id,
                pollNumber=pollNumber,
                ballotGuid = guid,
                electionOfficialJmbg=jmbg
            )

            database.session.add(vote);
            database.session.commit();
            print("dodato u vote")
            return;


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True,host="0.0.0.0", port=5005);
