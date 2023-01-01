import requests,os, json
def make_dict(a):
    list = dict(a)
    for i in a:
        list[i] = dict(a[i])
    return list

def is_following(username):
    r = requests.post("https://replit.com/graphql", json = {
      	"query": """
            query userByUsername($username: String!) {
              userByUsername(username: $username) {
                isFollowingCurrentUser
                followCount
                followerCount
                isFollowingCurrentUser
                image
            }
        }
        """,
      		"variables": """{ "username": "%s" }""" % username
    },
    headers = {
        "X-Requested-With": "ReplitApi",
        "referer": "https://replit.com/",
        "User-Agent": "Mozilla/5.0",
        "Cookie": "connect.sid="+os.getenv('sid')+""
    })
    data = json.loads(r.text)["data"]["userByUsername"]
    return data