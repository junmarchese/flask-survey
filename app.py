from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret-survey!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

# Initialize a variable called responses to be an empty list

responses = []
RESPONSES_KEY = "responses"

@app.route("/")
def homepage():
    """Render a start page that shows user the survey title, instructions, and a button.  The button serves as a link to the questions route."""

    title = "Customer Satisfaction Survey"
    instructions = "Please fill out a survey about your experience with us."
   
    return render_template("start.html", title=title, instructions=instructions if "/" in request.path else None)

@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses to create new session and redirect"""

    session[RESPONSES_KEY] = []
    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_answer():
    """Handle POST request to store user's answer and redirect to next question."""
    
    # get response choice
    choice = request.form["answer"]

    # add response to the session
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    #Check if more questions remain.  If all questions are answered, then redirect to "Thank You!" page.  Otherwise, redirect to next question.
    
    if (len(responses) == len(satisfaction_survey.questions)):
        return redirect("/thankyou")
    else:
        return redirect(f"/questions/{len(responses)}")



@app.route("/questions/<int:question_num>")
def handle_question(question_num):
    """Render the question page to show current question or look for a specific question number."""

    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        # access question page too soon
        return redirect("/")
    
    if (len(responses) == len(satisfaction_survey.questions)):
        # all questions are answered. Send users to thank you page
        return redirect("/thankyou")
    
    if (question_num >= len(satisfaction_survey.questions)):
        # access question number beyond the total number of questions
        flash(f"Invalid question number: {question_num}.")
        return redirect(f"/questions/{len(responses)}")

    if (len(responses) != question_num):
        # access questions out of order
        flash(f"Invalid question number: {question_num}.")
        return redirect(f"/questions/{len(responses)}")
        # next_question = min(question_num, len(satisfaction_survey.questions))
        # return redirect(f"/questions/{next_question}")
    
    question = satisfaction_survey.questions[question_num]
    return render_template("question.html", question_num=question_num, question=question)

    
@app.route("/thankyou")
def complete():
    """Show completion page that displays thank you message after survey is completed."""

    return render_template("thankyou.html")


if __name__ == "__main__":
    app.run(debug=True)