from flask import Flask, request, jsonify, Response;
from configuration import Configuration;
from models import database, User, UserRole;
from sqlalchemy import and_;
import re;
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity;
from adminDecorator import roleCheck;

application = Flask (__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);

@application.route("/", methods=["GET"])
def test_image():
    return "Authentication image working!";

def check_password(password):
    # string od najvise 256 karaktera, minimalno 8 znakova, bar jedna cifra, jedno malo i veliko slovo
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,256}$";
    result = re.match(regex,password);
    return result;

def check_email(email):
    regex = r"^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,3}$";
    result = re.match(regex,email);
    return result;

def check_jmbg(jmbg):
    regex = r"^[0-9]+$";
    result = re.match(regex, jmbg);
    if (not result): return False;
    # DDMMYYYRRBBBK = abcdefghijklm
    a = int(jmbg[0]);
    b = int(jmbg[1]);
    c = int(jmbg[2]);
    d = int(jmbg[3]);
    e = int(jmbg[4]);
    f = int(jmbg[5]);
    g = int(jmbg[6]);
    h = int(jmbg[7]);
    i = int(jmbg[8]);
    j = int(jmbg[9]);
    k = int(jmbg[10]);
    l = int(jmbg[11]);
    entered_m = int (jmbg[12]);

    result = False;

    dd = a*10 + b;
    print(dd);
    mm = c*10 + d;
    print(mm);
    yyy = e*100 + f*10 + g;
    print(yyy);
    rr = h*10 + i;
    print(rr);
    bbb = j*100 + k*10 + l;
    print(bbb);
    if ( 1 <= dd <= 31):
        result = True;
    else: return False;

    if ( 1 <= mm <= 12):
        result = True;
    else: return False;

    if ( 0 <= yyy <= 999):
        result = True;
    else: return False;

    if ( 70 <= rr <= 99):
        result = True;
    else: return False;

    if ( 0 <= bbb <= 999):
        result = True;
    else: return False;

    m = 11 - ((7*(a + g) + 6*(b + h) + 5*(c + i) + 4*(d + j) + 3*(e + k) + 2*(f + l) ) % 11);
    print(m);
    if (m == 10 or m == 11):
        m=0;

    if ( m == entered_m):
        result = True;
    else: result = False;

    return result;

@application.route("/delete", methods=["POST"])
@roleCheck(role ="admin")
@jwt_required()
def delete():
    email = request.json.get("email", "")

    emailEmpty = len(email) == 0;

    message = "";

    if (emailEmpty):
        message="Field email is missing.";
    elif (not check_email(email)):
        message="Invalid email.";

    if (message != ""):
        return jsonify(message = message), 400;

    user = User.query.filter(User.email == email).first();

    if (not user):
        message="Unknown user.";

    if (message != ""):
        return jsonify(message = message), 400;

    database.session.delete(user);
    database.session.commit();

    return Response (status = 200);

@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):
    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );

    additionalClaims = {
            "jmbg" :refreshClaims["jmbg"],
            "forename" : refreshClaims["forename"],
            "surname" : refreshClaims["surname"],
            "roles" : refreshClaims["roles"]
    };
    accessToken = create_access_token(identity = identity, additional_claims = additionalClaims);
    return jsonify ( accessToken = accessToken), 200;

@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;

    message = "";

    if (emailEmpty):
        message="Field email is missing.";
    elif (passwordEmpty):
        message="Field password is missing."
    elif (not check_email(email)):
        message="Invalid email.";

    if (message != ""):
        return jsonify(message = message), 400;

    user = User.query.filter(and_(User.email == email, User.password == password)).first();

    if (not user):
        message="Invalid credentials.";

    if (message != ""):
        return jsonify(message = message), 400;

    additionalClaims = {
        "jmbg": user.jmbg,
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);


    return jsonify(accessToken = accessToken, refreshToken = refreshToken), 200


@application.route("/register", methods=["POST"])
def register ():
    jmbg = request.json.get("jmbg", "");
    forename = request.json.get("forename", "");
    surname = request.json.get("surname", "");
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    message = "";

     #Prva provjera da li su sva polja prisutna

    jmbgEmpty = len(jmbg) == 0
    forenameEmpty = len(forename) == 0;
    surnameEmpty = len(surname) == 0;
    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;

    if (jmbgEmpty):
        message = "Field jmbg is missing.";
    elif (forenameEmpty):
        message = "Field forename is missing.";
    elif (surnameEmpty):
        message = "Field surname is missing.";
    elif (emailEmpty):
        message = "Field email is missing.";
    elif (passwordEmpty):
        message = "Field password is missing.";
    #Druga provjera jmbg format
    elif (not check_jmbg(jmbg)):
        message = "Invalid jmbg.";
    #Treca provjera email format
    elif (not check_email(email)):
        message = "Invalid email.";
    #Cetvrta provjera password format
    elif (not check_password(password)):
        message = "Invalid password.";

    if (message != ""):
            return jsonify(message = message), 400;

    #Peta provjera postojanje email-a u bazi
    user = User.query.filter(User.email == email).first();
    if (user):
        message="Email already exists.";

    if (message != ""):
        return jsonify(message = message), 400;

    user = User(
        jmbg = jmbg,
        forename = forename,
        surname = surname,
        email = email,
        password = password
    );

    database.session.add(user);
    database.session.commit();

    userRole = UserRole (userId= user.id, roleId = 2);
    database.session.add(userRole);
    database.session.commit();
    return Response(status = 200);

if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True,host="0.0.0.0" ,port=5002);