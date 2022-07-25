import logging

import requests as req

# init some var

_appid = "wx9b4c1a02cb364d08"

_secret_id = "7f3bdde2b0c1d33d84524c1d3df4bb75"


def get_access_token(appid=_appid, secret_id=_secret_id):
    url = \
        "https://api.weixin.qq.com/cgi-bin/token?" \
        "grant_type=client_credential" \
        "&appid={}" \
        "&secret={}".format(appid, secret_id)

    res = req.get(url)

    print(res)

    return res.json()["access_token"]


def get_openid(u_code, appid=_appid, secret_id=_secret_id):
    url = "https://api.weixin.qq.com/sns/jscode2session?" \
          "appid={}" \
          "&secret={}" \
          "&js_code={}" \
          "&grant_type=authorization_code".format(_appid, _secret_id, u_code)

    res = req.get(url=url)
    res.encoding = 'ascii'
    try:
        out = res.json()["openid"]
        return out
    except:
        logging.warning(res.json()["errmsg"])
        return None
