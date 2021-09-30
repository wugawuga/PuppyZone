from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from datetime import datetime

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta

# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/zone')
def zone():
    return render_template('zone.html')

@app.route('/zone-detail')
def zonedetail():
    return render_template('zone-detail.html')

@app.route('/snspet')
def snspet():
    return render_template('snspet.html')

@app.route('/snspet-detail')
def snspetdetail():
    return render_template('snspet-detail.html')



@app.route('/sns', methods=['GET'])
def listing():
    snss = list(db.sns.find({},{'_id': False}))
    return jsonify({'all_snss': snss})

## API 역할을 하는 부분
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

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)