from flask import Flask, render_template, request, redirect, url_for
import praw
import smtplib
import utils, base64, datetime, time
import threading


app = Flask(__name__)


@app.route("/")
def index():
    email = request.args.get("email", "null")
    return render_template("index.html")


@app.route("/send")
def send_mail():
    input_email = request.args.get("email", "null")
    thread = threading.Thread(target=weekly_email, args=(input_email,))
    thread.start()
    return redirect(url_for("index"))


def weekly_email(input_email):
    print("Sending...")
    make_mail(input_email)
    print("Waiting to send another email...")
    send_time = datetime.datetime.utcnow()
    interval = datetime.timedelta(weeks=1)
    while True:
        send_time = send_time + interval
        time.sleep((send_time.timestamp()) - time.mktime(time.gmtime(time.time())))
        print("Sending email")
        make_mail(input_email)
        print("Waiting to send another email...")


def make_mail(input_email):
    movie_detail = get_movie_detail()
    send_to = input_email
    email = "dev.shahjr@gmail.com"
    password = utils.password

    print("Fetching the highest rated movie from r/MovieSuggestions")

    subject = f"[Suggestion Bot] {movie_detail['title']} - r/MovieSuggestions"
    body = f"Hi {send_to.split(sep='@')[0]},\n\n{movie_detail['text']}"
    mail = f"Subject: {subject}\n\n{body} - by {movie_detail['author']}.\n\nThanks,\nWeekly top rated movie\nAutomated email using python."

    print("Establishing a SMTP connection")

    conn = smtplib.SMTP("smtp.gmail.com", 587)
    conn.ehlo()
    conn.starttls()
    conn.ehlo()
    conn.login(email, base64.b64decode(password).decode("utf-8"))
    conn.sendmail(email, send_to, mail)

    print("Sucessful, check your inbox!")
    conn.quit()


def get_movie_detail():
    reddit = praw.Reddit(
        client_id="BSxCJm9uPRKkwQ",
        client_secret="ZOTBhDsxqxL4_UJWZn4pLVdM4ek",
        user_agent="u/ShahJr",
    )

    subreddit = reddit.subreddit("MovieSuggestions")

    movie_detail = {"title": None, "text": None, "author": None}
    for submission in subreddit.search(
        'flair:"SUGGESTING"', sort="top", time_filter="week", limit=1
    ):
        movie_detail["title"] = submission.title
        movie_detail["text"] = submission.selftext
        movie_detail["author"] = str(submission.author)

    return movie_detail

if __name__ == "__main__":
    app.run(debug=True)

# set FLASK_DEBUG=1, set FLASK_APP=application.py
