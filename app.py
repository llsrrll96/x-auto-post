from flask import Flask, render_template, request, redirect, url_for
import tweepy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

# Twitter API 인증 정보
api_key = ''
api_secret = ''
access_token = ''
access_token_secret = ''
client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token,
                       access_token_secret=access_token_secret)

# 전송된 트윗과 예약된 트윗 정보를 저장할 리스트
sent_tweets = []
scheduled_tweets = []

# APScheduler 설정
scheduler = BackgroundScheduler()
scheduler.start()

def tweet_job(tweet_content):
    if tweet_content:
        client.create_tweet(text=tweet_content)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 전송된 트윗 정보를 리스트에 추가
        sent_tweets.append({'content': tweet_content, 'timestamp': timestamp})

        print("트윗이 성공적으로 게시되었습니다!: ", timestamp, tweet_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tweet', methods=['POST'])
def schedule_tweet():
    tweet_content = request.form['tweet']
    print(tweet_content)
    client.create_tweet(text=tweet_content)

    # 전송된 트윗 정보를 리스트에 추가
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sent_tweets.append({'content': tweet_content, 'timestamp': timestamp})

    return "tweet: 트윗이 전송완료"

@app.route('/schedule-tweet', methods=['POST'])
def schedule_tweet_func():
    global scheduled_tweets
    tweet_content = request.form['tweet']
    schedule_time = request.form['scheduleTime']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 고유 ID 생성 (임시로 timestamp 사용)
    tweet_id = len(scheduled_tweets) + 1

    # 스케줄링 설정
    scheduler.add_job(tweet_job, 'cron', args=[tweet_content], hour=schedule_time.split(':')[0], minute=schedule_time.split(':')[1])

    # 예약된 트윗 정보를 리스트에 추가
    scheduled_tweets.append({
        'content': tweet_content,
        'time': schedule_time,
        'timestamp': timestamp,
        'id': tweet_id
    })

    return redirect(url_for('get_scheduled_tweets'))

@app.route('/scheduled-tweets', methods=['GET'])
def get_scheduled_tweets():
    return render_template('scheduled_tweets.html', scheduled_tweets=scheduled_tweets, sent_tweets=sent_tweets)

@app.route('/api-settings', methods=['GET', 'POST'])
def api_settings():
    global api_key, api_secret, access_token, access_token_secret, client

    if request.method == 'POST':
        api_key = request.form['api_key']
        api_secret = request.form['api_secret']
        access_token = request.form['access_token']
        access_token_secret = request.form['access_token_secret']

        # 클라이언트 재설정
        client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token,
                               access_token_secret=access_token_secret)

        return redirect(url_for('api_settings'))

    return render_template('api_settings.html', api_key=api_key, api_secret=api_secret,
                           access_token=access_token, access_token_secret=access_token_secret)

if __name__ == '__main__':
    app.run(debug=True)
