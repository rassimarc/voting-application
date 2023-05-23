from flask import Flask, render_template, request, Response, make_response
import datetime
import pandas as pd

app = Flask(__name__)
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
data = pd.read_csv("questions.csv", encoding="utf-8")
print(data)
num_rows = data.shape[0]
num_columns = data.shape[1]
time = datetime.datetime(2020, 1, 1, 1, 1, 1, 1)

# Access the data in each row and column
for i in range(num_rows):
    Questions[i+1] = data.iloc[i, 0]
    Answers[i+1] = data.iloc[i, 1:len(data.iloc[i, :])]
"""
try:
    while True:
        namehandle = open(f"test-question{i}.txt", mode='r', encoding="utf-8")
        L = namehandle.readlines()
        Questions[i] = L[0]
        Answers[i] = L[1:len(L)]
        i += 1
except:
    pass
    """
@app.route('/')
def index():
    session["isOpen"] = True
    global time
    time = datetime.datetime.now()
    return "Hello"

@app.route('/question')
def questions():
    activeID = session["activeQuestion"]
    activeQuestion = Questions[activeID]
    activeAnswers = Answers[activeID]
    isOpen = session["isOpen"]
    if f'voted{activeID}' in request.cookies:
        return render_template("voted.html", Question = activeQuestion, x = activeAnswers)
    if isOpen: 
        return render_template("question.html", Question = activeQuestion, x = activeAnswers)
    else: return "Stay Tuned!"

@app.route('/vote', methods = ["POST"])
def vote():
    otherTime = datetime.datetime.now()
    activeID = session["activeQuestion"]
    activeQuestion = Questions[activeID]
    activeAnswers = Answers[activeID]
    timeDifference = otherTime - time
    isOpen = session["isOpen"]

    if timeDifference.seconds > 10:
        session["isOpen"] = False
        return Response("Voting is closed", status=400)

    if not isOpen:
        return Response("Voting is closed", status=400)

    option = request.form.get('answer')

    if not option:
        return Response("Invalid option", status=400)

    if f'voted{activeID}' in request.cookies:
        return Response("You have already voted", status=400)

    try:
        session[option] += 1
        response = make_response(render_template("thanks.html",  question = activeQuestion, options = activeAnswers, votes = [session["1"], session["2"], session["3"], session["4"]]))
        # Set a cookie to mark the user as voted
        response.set_cookie(f'voted{activeID}', 'true')
        return response 
    except:
        return Response("Bad request", 400)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

