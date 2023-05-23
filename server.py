from flask import Flask, render_template, request, Response, make_response


app = Flask(__name__)
session = {}
Questions = {}
Answers = {}
session["activeQuestion"] = 3
session[f'1'] = 0
session[f'2'] = 0
session[f'3'] = 0
session[f'4'] = 0
session["isOpen"] = True
i = 1
try:
    while True:
        namehandle = open(f"test-question{i}.txt", mode='r', encoding="utf-8")
        L = namehandle.readlines()
        Questions[i] = L[0]
        Answers[i] = L[1:len(L)]
        i += 1
except:
    pass
    
@app.route('/')
def index():
    return "Hello"

@app.route('/question')
def questions():
    activeID = session["activeQuestion"]
    activeQuestion = Questions[activeID]
    activeAnswers = Answers[activeID]
    isOpen = session["isOpen"]
    if f'voted{activeID}' in request.cookies:
        return render_template("voted.html", Question = activeQuestion, x = activeAnswers)
    if isOpen: return render_template("question.html", Question = activeQuestion, x = activeAnswers)
    else: return "Stay Tuned!"

@app.route('/vote', methods = ["POST"])
def vote():
    activeID = session["activeQuestion"]
    activeQuestion = Questions[activeID]
    activeAnswers = Answers[activeID]

    isOpen = session["isOpen"]

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

