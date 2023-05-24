from flask import Flask, render_template, request, Response, make_response
import datetime
import pandas as pd
import time
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('voting-v0.1.db')
session = {}
Questions = {}
Answers = {}
session["activeQuestion"] = 5
session['1'] = 0
session['2'] = 0
session['3'] = 0
session['4'] = 0
session["isOpen"] = True
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
            A[i+1] = data.iloc[i, 1:len(data.iloc[i, :])].to_list()
    except Exception as exp:
        print("Failed to read the question file", exp)

    return Q, A

Questions, Answers = csv_open()

@app.route('/')
def index():
    global _time
    _time = time.time()
    return render_template("index.html")

@app.route("/admin", methods = ['GET', 'POST'])
def question_options():
    if request.method == "GET":
        return render_template("settings.html", QuestionNumber = list(Questions.keys()), Questions = Questions)
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
        return render_template("settings.html", QuestionNumber = list(Questions.keys()), Questions = Questions)



@app.route('/question')
def questions():
    activeID = session["activeQuestion"]
    activeQuestion = Questions.get(activeID, "")
    activeAnswers = Answers.get(activeID, [])
    if not activeAnswers or not activeQuestion :
        return "There are no questions"
    isOpen = session["isOpen"]
    if not isOpen:
        return "Stay Tuned!"
    if f'voted{activeID}' in request.cookies:
        return render_template("voted.html", Question = activeQuestion, x = activeAnswers) 
    return render_template("question.html", Question = activeQuestion, x = activeAnswers, timer = _time-time.time())

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
        response = make_response(render_template("thanks.html",  question = activeQuestion, options = activeAnswers, votes = [session["1"], session["2"], session["3"], session["4"]]))
        # Set a cookie to mark the user as voted
        response.set_cookie(f'voted{activeID}', 'true')
        return response 
    except:
        return Response("Bad request", 400)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)

