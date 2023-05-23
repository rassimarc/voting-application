from flask import Flask, render_template, request, Response
import io


app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        namehandle = io.open("test-question.txt", mode='r', encoding="utf-8")
        L=[]
        for line in namehandle:
            L.append(line)
        return render_template("question.html", question = L[0], answer1 = L[1], answer2 = L[2], answer3= L[3], answer4 = L[4])
    else:
        try:
            answer = request.form["answer"]
            return render_template("thanks.html", answer = answer)
        except:
            return Response("Bad request", 400)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

