import requests
import praw
import smtplib
import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def get_movie_detail():
        reddit = praw.Reddit(client_id="BSxCJm9uPRKkwQ",
                     client_secret="ZOTBhDsxqxL4_UJWZn4pLVdM4ek",
                     user_agent="u/ShahJr")

        subreddit = reddit.subreddit('MovieSuggestions')
        
        movie_detail = {'title': None, 'text': None, 'author':None}
        for submission in subreddit.search('flair:"SUGGESTING"',sort='top',time_filter='week',limit=1):
                movie_detail['title'] = submission.title
                movie_detail['text'] = submission.selftext
                movie_detail['author'] = str(submission.author)

        return movie_detail


def get_subscribed_users():
    api_key = os.environ.get("MAILGUN_API_KEY")

    url = f"https://api:{api_key}@api.mailgun.net/v3/lists/dev.shahjr@sandbox7cd5b792c64c4d4ab943128c646c5234.mailgun.org/members"

    response = requests.get(url).json()
    print(requests.get(url).raise_for_status)

    data_list = response["items"]
    email_list = []
    for dict in data_list:
        email_list.append(dict["address"])

    return email_list


def send_mail():
        email = 'dev.shahjr@gmail.com'
        password = 'Herald54321@##'
        print("Fetching email of subscirbed users")
        send_to = get_subscribed_users()

        print("Fetching the highest rated movie from r/MovieSuggestions")
        movie_detail = get_movie_detail()

        subject = f"[Suggestion Bot] {movie_detail['title']} - r/MovieSuggestions"
        # body = f"Hi {send_to.split(sep='@')[0]},\n\n{movie_detail['text']}"
        body = f"Hi there,\n\n{movie_detail['text']}"
        mail = f"Subject: {subject}\n\n{body} - by {movie_detail['author']}.\n\nThanks,\nWeekly top rated movie\nAutomated email using python"

        print("Establishing a SMTP connection")
        
        conn = smtplib.SMTP('smtp.gmail.com',587)
        conn.ehlo()
        conn.starttls()
        conn.ehlo()
        conn.login(email, password)

        for user in send_to:
            print("Sending email to " + user)
            conn.sendmail(email, user, mail.encode("utf-8"))

        print("Sucessful, check your inbox!")
        conn.quit()


today = datetime.date.today()
if today.isoweekday() == 5:
    print("Sending weekly newsletter.")
    send_mail()



# send_time = datetime.datetime.utcnow()
# interval = datetime.timedelta(minutes=1)
# while True:
#         send_time = send_time + interval
#         time.sleep((send_time.timestamp()) - time.mktime(time.gmtime(time.time())))
#         print('Sending email')
#         send_mail()
#         print('email sent')