from flask import Flask, redirect, render_template, url_for, request
from replit import web, db
import requests,random,sys
from fun import make_dict,is_following
from better_profanity import profanity
app = Flask(__name__)
user = web.UserStore()

@app.route("/")
@web.authenticated_template("login.html")
def home():
    new = "false"
    if web.auth.name not in db["names"]:
        user.current["tasks"] = {}
        db["names"].append(web.auth.name)
        new = "true"
    try:
        user.current["apps"]
    except:
        user.current["apps"] = {}
    return render_template("home.html",apps=make_dict(user.current["apps"]),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name,is_new=new)

@app.route("/calculator")
@web.authenticated_template("login.html")
def calc():
    return render_template("maths.html",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/games")
@web.authenticated_template("login.html")
def games():
    return render_template("game.html",apps=make_dict(user.current["apps"]),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/games/play/<game>")
@web.authenticated_template("login.html")
def play(game):
    return render_template("play.html",game=game.title(),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/tasks")
@web.authenticated_template("login.html")
def tasks():
    return render_template("tasks.html",tasks = make_dict(user.current["tasks"]),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/tasks/new",methods=["POST","GET"])
@web.authenticated_template("login.html")
def task_new():
    if request.method == "POST":
        follow = is_following(web.auth.name)["isFollowingCurrentUser"]
        print(sys.getsizeof(user.current["tasks"]))
        if (follow == True and sys.getsizeof(user.current["tasks"]) < 2000) or (follow == False and sys.getsizeof(user.current["tasks"]) < 1000):
            title  = profanity.censor(request.form["title"])
            desc  = profanity.censor(request.form["desc"])
            date  = profanity.censor(request.form["date"])
            if len(title) > 80 or len(desc) > 200 or len(date) > 15 or len(title) == 0 or len(desc) == 0:
                return "Inputs are to long or short"
            id = random.randint(1,10000000)
            while id in user.current["tasks"]:
                id = random.randint(1,10000000000)
            user.current["tasks"][id] = {"title":title,"desc":desc,"date":date}
        else:
            return "You do not have space"
    return redirect("/tasks")

@app.route("/tasks/edit/<id>",methods=["POST","GET"])
@web.authenticated_template("login.html")
def task_edit(id):
    if request.method == "POST":
        title  = profanity.censor(request.form["title"])
        desc  = profanity.censor(request.form["desc"])
        date  = profanity.censor(request.form["date"])
        if len(title) > 80 or len(desc) > 200 or len(date) > 15 or len(title) == 0 or len(desc) == 0:
            return "Inputs are to long or short"
        user.current["tasks"][id] = {"title":title,"desc":desc,"date":date}
    return redirect("/tasks")

@app.route("/tasks/del/<id>")
@web.authenticated_template("login.html")
def task_del(id):
    del user.current["tasks"][id]
    return redirect("/tasks")

@app.route("/appstore")
@web.authenticated_template("login.html")
def app_store():
    return render_template("apps.html",apps=make_dict(db["apps"]),name=web.auth.name,boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"])

@app.route("/appstore/new", methods=["POST","GET"])
@web.authenticated_template("login.html")
def new_app():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        url = request.form["url"]
        img_url = request.form["img_url"]
        tag = request.form["tag"]
        name = 0
        boosting = is_following(web.auth.name)["isFollowingCurrentUser"]
        for i in db["apps"]:
            if db["apps"][i]["user"] == web.auth.name:
                name += 1
        for i in db["review"]:
            if db["review"][i]["user"] == web.auth.name:
                name += 1
        if (name >= 2 and boosting == False) or (name >= 4 and boosting == True):
            return render_template("apps_new.html",error="You reached your maxamem amount of apps.",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
        if len(title) < 1 or len(desc) < 1 or len(url) < 1 or len(img_url) < 1 or len(tag) < 1:
            return render_template("apps_new.html",error="You Need More Info",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
        manifest = requests.get(url+"/manifest.json")
        img = requests.get(img_url)
        if manifest.status_code == 200 and img.status_code == 200:
            json = manifest.json()
            if json["name"] == title and json["desc"] == desc:
                if profanity.contains_profanity(title+" "+desc+" "+url+" "+img_url+" "+tag) == True:
                    return render_template("apps_new.html",error="You App Might Contain Profanity",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
                elif title in db["apps"] or title in db["review"]:
                     return render_template("apps_new.html",error="App Name Is In Use",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
                else:
                    print(title)
                    db["review"][title] = {"title":title,"desc":desc,"url":url,"img":img_url,"tag":tag,"user":web.auth.name,"featured":False}
                    return redirect("/appstore")
            else:
                return render_template("apps_new.html",error="Manifest Incomplete",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
        else:
            return render_template("apps_new.html",error="Page Not Found Or Image Not Found",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
    return render_template("apps_new.html",error=False,boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/review")
@web.authenticated_template("login.html")
def review():
    if web.auth.name == "GoodVessel92551":
        return render_template("review.html",apps=make_dict(db["review"]),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
    else:
        return redirect("/")

@app.route("/review/remove/<name>")
@web.authenticated_template("login.html")
def review_remove(name):
    if web.auth.name == "GoodVessel92551":
        del db["review"][name]
        return redirect("/review")
    else:
        return redirect("/")

@app.route("/review/<name>")
@web.authenticated_template("login.html")
def review_app(name):
    if web.auth.name == "GoodVessel92551":
        url = db["review"][name]["url"]
        if url[-1] == "/":
            html = requests.get(url+"index.html")
            script = requests.get(url+"script.js")
            css = requests.get(url+"style.css")
        else:
            html = requests.get(url+"/index.html")
            script = requests.get(url+"/script.js")
            css = requests.get(url+"/style.css")
        if html.status_code != 200 or script.status_code != 200 or css.status_code != 200:
            return "error"
        else:
            html = html.text
            script = script.text
            css = css.text
            return render_template("review_app.html",html=html,script=script,css=css,name=name,boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"])
    else:
        return redirect("/")

@app.route("/star/<name>")
@web.authenticated_template("login.html")
def star(name):
    if web.auth.name == "GoodVessel92551":
        if db["review"][name]["featured"] == False:
            db["review"][name]["featured"] = True
        else:
            db["review"][name]["featured"] = False
        return redirect("/review/"+name)
    return redirect("/")

@app.route("/upload/<name>")
@web.authenticated_template("login.html")
def upload(name):
    if web.auth.name == "GoodVessel92551":
        db["apps"][name] = db["review"][name]
        del db["review"][name]
        return redirect("/appstore")
    else:
        return redirect("/")

@app.route("/app/<name>")
@web.authenticated_template("login.html")
def run_app(name):
    url = db["apps"][name]["url"]
    title = db["apps"][name]["title"]
    return render_template("veiw_app.html",url=url,title=title,apps=make_dict(db["review"]),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/preview/<name>")
@web.authenticated_template("login.html")
def peview(name):
    if web.auth.name == "GoodVessel92551":
        url = db["review"][name]["url"]
        title = db["review"][name]["title"]
        return render_template("veiw_app.html",url=url,title=title,apps=make_dict(db["review"]),boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)
    else:
        return redirect("/")

@app.route("/download/<name>")
@web.authenticated_template("login.html")
def download(name):
    user.current["apps"][name] = db["apps"][name]
    return redirect("/")

@app.route("/remove/<name>")
@web.authenticated_template("login.html")
def remove(name):
    if web.auth.name == "GoodVessel92551":
        del db["apps"][name]
    return redirect("/appstore")

@app.route("/delete/<name>")
@web.authenticated_template("login.html")
def delete(name):
    del user.current["apps"][name]
    return redirect("/")

@app.route("/boost")
@web.authenticated_template("login")
def boost():
    return render_template("boost.html",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/mail")
@web.authenticated_template("login.html")
def mail():
    return render_template("mail.html",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/revise")
@web.authenticated_template("login.html")
def revise():
    return render_template("revise.html",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/time")
@web.authenticated_template("login.html")
def time():
    return render_template("time.html",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

@app.route("/dice")
@web.authenticated_template("login.html")
def dice():
    return render_template("dice.html",boosting=is_following(web.auth.name)["isFollowingCurrentUser"],profile_pic=request.headers["X-Replit-User-Profile-Image"],name=web.auth.name)

app.run(host="0.0.0.0",port=81,debug=True)