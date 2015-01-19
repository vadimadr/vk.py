from collections import deque
from datetime import datetime
import json
import webbrowser
import re
import os
import time
from urllib.parse import urlencode
import urllib.request as req


def flatten(it):
    result = []
    for i in it:
        if type(i) is list:
            result += flatten(i)
        else:
            result.append(i)
    return result


class VkApiError(Exception):
    def __init__(self, data, method, args):
        self.code = data['error_code']
        self.description = data['error_msg']
        self.method = method
        self.args = args

    def __str__(self):
        return "%s: %s" % (self.code, self.description)


class VkApi:
    """
    Оболочка для api vk.com.
    """

    def __init__(self, key, limit=5):
        self.limit = limit
        self.queries = deque(maxlen=limit)
        self.key = key
        self.count = 0

    def method(self, method, spam_if_fail=True, **args):
        payload = {'access_token': self.key}
        payload.update(args)
        request_url = ('https://api.vk.com/method/%s?%s' % (method, urlencode(payload))).replace('\'', '\"')

        if len(self.queries) >= self.limit and (datetime.now() - self.queries[0]).total_seconds() < 1:
            time.sleep(1.1)
            self.queries.clear()

        response = req.urlopen(request_url)
        encoding = response.headers.get_content_charset()
        data = json.loads(response.read().decode(encoding))
        self.queries.append(datetime.now())

        if 'error' in data:

            if spam_if_fail and data['error']['error_code'] == 6:
                time.sleep(1.5)
                return self.method(method, spam_if_fail=spam_if_fail, **args)
            else:
                raise VkApiError(data['error'], method, args)
        else:
            return data['response']

    def execute(self, method, list_vars, calls_per_request=12, **kwargs):
        if not type(list_vars) is list:
            list_vars = [list_vars]
        list_args = {k: kwargs.pop(k) for k in list_vars}
        counter = list_vars[0]

        args = {k: v for k, v in kwargs.items() if type(v) is not list}
        args.update({k: '_%s.shift()' % k for k in list_vars})
        args_encoded = '{%s}' % ','.join('%s:%s' % (k, v) for k, v in args.items())
        src = '{lvars};var __r=[];while(_{counter}){{__r.push(API.{method}({args}));}}return __r;'

        i = calls_per_request
        result = []

        while list_args[counter]:
            lvr = ["var _{}={}".format(k, v[:i]) for k, v in list_args.items()]
            lvars = ';'.join(lvr)
            script = src.format(lvars=lvars, args=args_encoded, method=method, counter=counter)
            # print(script)

            for k in list_args:
                list_args[k] = list_args[k][i:]
            i += calls_per_request
            dr = self.method('execute', code=script.replace('\'', '\"'))
            result += flatten(dr)

        return result

    def load(self, method, count, delta, **kwargs):
        idx = list(range(0, count, delta))
        return self.execute(method, 'offset', offset=idx, count=delta, **kwargs)

    @staticmethod
    def get_auth_url(app_id, permissions='', api_version='5.27'):
        payload = {
            'client_id': app_id,
            'scope': permissions,
            'redirect_uri': 'https://oauth.vk.com/blank.html',
            'display': 'page',
            'v': api_version,
            'response_type': 'token'
        }
        return 'https://oauth.vk.com/authorize?%s' % urlencode(payload)

    @classmethod
    def browser_auth(cls, app_id, permissions='', api_version='5.27', limit=5):
        auth_url = cls.get_auth_url(app_id, permissions, api_version)
        print(u"Пройдите авторизацию и скопируйте url из адресной строки. ")
        old_d = os.dup(1)
        os.close(1)
        os.open(os.devnull, os.O_RDWR)
        try:
            webbrowser.open_new_tab(auth_url)
        finally:
            os.dup2(old_d, 1)
        key = input("Url: ")
        return cls.from_redirect_uri(key, limit)

    @classmethod
    def from_redirect_uri(cls, uri, limit=5):
        pattern = re.compile(r'access_token=([a-fA-F0-9]+)(?:\Z|&)')
        parsed = pattern.search(uri)
        token = parsed.group(1) if parsed else None
        return cls(token, limit)

