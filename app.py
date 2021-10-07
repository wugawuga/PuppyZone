from pymongo import MongoClient
import jwt
import datetime
import hashlib
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
cafedata = requests.get('https://www.diningcode.com/list.php?query=%EC%84%9C%EC%9A%B8%20%EC%95%A0%EA%B2%AC%EB%8F%99%EB%B0%98%20%EC%B9%B4%ED%8E%98',headers=headers)
zonecf = BeautifulSoup(cafedata.text, 'html.parser')


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.puppyzone

# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/main2')
def main2():
    return render_template('main2.html')

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html')
    
@app.route('/zone')
def zone():
    return render_template('zone.html')

@app.route('/zone2')
def zone2():
    return render_template('zone2.html')

@app.route('/zone-detail')
def zonedetail():
    return render_template('zone-detail.html')

@app.route('/snspet')
def snspet():
    return render_template('snspet.html')

@app.route('/snspet2')
def snspet2():
    return render_template('snspet2.html')

@app.route('/snspet-detail')
def snspetdetail():
    return render_template('snspet-detail.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/about2')
def about2():
    return render_template('about2.html')


@app.route('/')
def logining():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # Client info 보내주기
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
        'id': username_receive,
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입 Server
@app.route('/sign_up/save', methods=['POST'])
def sign_up():

    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }

    db.users.insert_one(doc)

    return jsonify({'result': 'success'})

# id 중복확인 Server
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sns', methods=['GET'])
def listing():
    snss = list(db.sns.find({},{'_id': False}))
    return jsonify({'all_snss': snss})

# zone.html 카드
@app.route('/show_cafe', methods=['GET'])
def showcafe():
    cafe = list(db.cafes.find({}, {'_id': False}))
    return jsonify({'cafes': cafe})

# zone.html 카드
@app.route('/show_pension', methods=['GET'])
def showpension():
    pension = list(db.pensions.find({}, {'_id': False}))
    return jsonify({'pensions': pension})

@app.route('/show_rice', methods=['GET'])
def showrice():
    rice = list(db.rices.find({}, {'_id': False}))
    return jsonify({'rices': rice})

@app.route('/show_playground', methods=['GET'])
def showplayground():
    playground = list(db.playgrounds.find({}, {'_id': False}))
    return jsonify({'playgrounds': playground})

@app.route('/show_play', methods=['GET'])
def showplay():
    play = list(db.plays.find({}, {'_id': False}))
    return jsonify({'plays': play})

@app.route('/show_hospital', methods=['GET'])
def showhospital():
    hospital = list(db.hospitals.find({}, {'_id': False}))
    return jsonify({'hospitals': hospital})

@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # Posting API
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]

        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "comment": comment_receive,
            "date": date_receive
        }

        db.posts.insert_one(doc)

        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/sns', methods=['POST'])
def saving():
    user_receive = request.form['user_give']
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']
    
    # File Area
    file = request.files["file_give"]

    # File에서 '.'으로 시작하는 것 중에서 맨 마지막 '.'만 들고와라!
    extension = file.filename.split('.')[-1]

    # 현재시각 Data
    today = datetime.now()

    # year/month/day/hour/minute/second
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    # File 이름 구분 짓기
    filename = f'file-{mytime}'

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)
    
    doc = {
        'user':user_receive,
        'title':title_receive,
        'file' : f'{filename}.{extension}',
        'comment':comment_receive,
        'like':0,
    }

    db.sns.insert_one(doc)

    return jsonify({'msg':'작성 완료!'})

@app.route('/api/like', methods=['POST'])
def like_star():
    user_receive = request.form['user_give']

    target_star = db.sns.find_one({'user': user_receive})
    current_like = target_star['like']

    new_like = current_like + 1

    db.sns.update_one({'user': user_receive}, {'$set': {'like': new_like}})

    return jsonify({'msg': '좋아요 완료!'})   

@app.route('/api/delete', methods=['POST'])
def delete_star():
    user_receive = request.form['user_give']

    db.sns.delete_one({'user': user_receive})

    return jsonify({'msg': '삭제 완료!'})

@app.route('/review', methods=['POST'])
def write_review():
    author_receive = request.form['author_give']
    review_receive = request.form['review_give']

    doc = {
        'author':author_receive,
        'review':review_receive
    }

    db.review.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


@app.route('/review', methods=['GET'])
def read_reviews():
    reviews = list(db.review.find({}, {'_id':False}))
    return jsonify({'all_reviews': reviews})

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)