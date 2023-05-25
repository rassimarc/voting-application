from flask import Flask, render_template, request, Response, make_response
import datetime
import pandas as pd
import time
import sqlite3
import os 

app = Flask(__name__)
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'voting-v0.1.db'))
cur = conn.cursor()

session = {}
Questions = {}
Questionss = []
Answers = {}
session["activeQuestion"] = 5
session['1'] = 0
session['2'] = 0
session['3'] = 0
session['4'] = 0
session["isOpen"] = False
i = 1
_time = 0

def csv_open():
    Q={}
    A={}
    try:
        data = pd.read_csv("questions.csv", encoding="utf-8")
        num_rows = data.shape[0]
        # Access the data in each row and column
        for i in range(num_rows):
            Q[i+1] = data.iloc[i, 0]
            try:
                cur.execute(f"INSERT INTO Question VALUES ({i+1}, '{Q[i+1]}', 0, 'marc' )")
                conn.commit()
            except Exception as exp:
                print("Could not insert question:", exp)
            A[i+1] = data.iloc[i, 1:len(data.iloc[i, :])].to_list()
            for j in range(len(A[i+1])):
                try:
                    cur.execute(f"INSERT INTO Option(op_id, op_content, op_votes, q_id) VALUES ({j+1}, '{A[i+1][j]}', 0, {i+1} )")
                    conn.commit()
                except Exception as exp:
                    print("Could not insert option:", exp)

    except Exception as exp:
        print("Failed to read the question file:", exp)

    return Q, A

Questions, Answers = csv_open()
conn.commit()

cur.execute("SELECT q_id, q_body FROM Question")
Questionss = cur.fetchall()
conn.close()

@app.route('/')
def index():
    global _time
    return render_template("index.html")

@app.route("/admin", methods = ['GET', 'POST'])
def question_options():
    if request.method == "GET":
        return render_template("settings.html", Questionss = Questionss)
    else:
        availability = request.form.get("mode")
        selected = request.form.get("selected")
        if selected:
            session["activeQuestion"] = int(selected)
        if availability == "Show":
            global _time
            _time = time.time()
            session["isOpen"] = True
        elif availability == "Hide":
            session["isOpen"] = False
        return render_template("settings.html", Questionss = Questionss)



@app.route('/question')
def questions():
    activeID = session["activeQuestion"]
    activeQuestion = Questions.get(activeID, "")
    activeAnswers = Answers.get(activeID, [])
    if not activeAnswers or not activeQuestion :
        return "There are no questions"
    isOpen = session["isOpen"]
    if not isOpen:
        return render_template("staytuned.html")
    if f'voted{activeID}' in request.cookies:
        return render_template("voted.html", Question = activeQuestion, x = activeAnswers) 
    return render_template("question.html", Question = activeQuestion, x = activeAnswers, timer = _time-time.time(), times = "loader 25s ease forwards")   

@app.route('/vote', methods = ["POST"])
def vote():
    isOpen = session["isOpen"]
    if not isOpen:
        return Response("Voting is closed", status=400)
    
    timeDifference = time.time() - _time
    if timeDifference > 60:
        session["isOpen"] = False
        return Response("Voting is closed", status=400)
    
    option = request.form.get('answer')
    if option not in ['1', '2', '3', '4']:
        return Response("Invalid option", status=400)

    activeID = session["activeQuestion"]
    if request.cookies.get(f'voted{activeID}'):
        return Response("You have already voted", status=400)
    
    
    activeQuestion = Questions[activeID]
    activeAnswers = Answers[activeID]

    try:
        session[option] += 1
        try:
            conn = sqlite3.connect('voting-v0.1.db')
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Option SET op_votes = op_votes + 1 WHERE q_id = {activeID} AND op_id = {option}")
            conn.commit()
            conn.close()
        except Exception as exp:
            print("Could not increment vote:", exp)
        # response = make_response(render_template("thanks.html",  question = activeQuestion, options = activeAnswers, votes = [session["1"], session["2"], session["3"], session["4"]]))
        response = make_response(Response("Thanks for voting", status=200))
        # Set a cookie to mark the user as voted
        response.set_cookie(f'voted{activeID}', 'true')
        return response 
    except:
        return Response("The vote could not be processed", 400)

@app.route('/results')
def results():
    activeID = session["activeQuestion"]
    activeQuestion = Questions[activeID]
    activeAnswers = Answers[activeID]
    try:
        conn = sqlite3.connect('voting-v0.1.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT op_votes FROM Option WHERE q_id = {activeID}")
        votes = cursor.fetchall()
        conn.close()
    except Exception as exp:
        print("Could not get votes:", exp)
    return render_template("thanks.html", question = activeQuestion, options = activeAnswers, votes = [session["1"], session["2"], session["3"], session["4"]])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
