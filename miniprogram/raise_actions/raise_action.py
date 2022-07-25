import logging
import requests as req

try:
    from get_cloud_info import get_access_token, get_openid
except Exception as e:
    logging.warning(repr(e))
    exit(-1)


class raise_action(object):
    url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token="

    drop_waring_id = "QF7DMRrSwOT9AXE5tR5dLkyRGAknPDrdQnPu7tPtNCA"

    pack_json_drop_warning = {
        "access_token": None,
        "touser": None,
        "template_id": "QF7DMRrSwOT9AXE5tR5dLkyRGAknPDrdQnPu7tPtNCA",
        "data": {
            "thing1": {
                "value": "老人摔倒提醒",
            },
            "name4": {
                "value": "",
            },
            "phrase5": {
                "value": "摔倒警告",
            },
            "thing2": {
                "value": "老人疑似摔倒了",
            },
        }
    }

    def __init__(self, ACCESS_TOKEN, ):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.url = self.url + ACCESS_TOKEN

        pass

    def raise_drop_warning(self, userid, tar_name="unknown"):
        tar = self.pack_json_drop_warning.copy()
        tar["data"]["name4"]["value"] = tar_name
        tar["access_token"] = self.ACCESS_TOKEN
        tar["touser"] = userid
        res = req.post(self.url, json=tar)
        print(res.text)
        logging.debug(res.json())
        pass


if __name__ == '__main__':
    # there is the test for usage
    token_id = get_access_token()
    user_id = "033Trb0000ilfO1MRW100ETNgk2Trb0O"
    openid = get_openid(user_id)
    act = raise_action(token_id)
    if openid is not None:
        act.raise_drop_warning(openid)
    pass
