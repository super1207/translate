import random
import requests
class formatcpp:
    '''用于将c++写的代码进行格式化
    '''
    def translate(self, word, to):
        data = {
            "data": word,
            'type': 'format',
            'arg': '1',
            'beforeSend': 'undefined'
        }
        ret = requests.post('http://web.chacuo.net/formatcpp', data=data)
        return ret.json()['data'][0]