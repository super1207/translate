import requests
import json
class runcpp:
    '''用于向一个在线运行CPP的网站发送代码，运行CPP
    '''
    @staticmethod
    def translate(data, args):
        args = (7,'cpp')
        if len(args) == 3:
            temp = data.splitlines()
            data1 = {'code': '\n'.join(temp[1::]), 'language': args[0], 'fileext': args[1], 'stdin': temp[0]}
        else:
            data1 = {'code': data,
                     'language': args[0], 'fileext': args[1]}
        headers = {'content-type': 'application/json',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        r = requests.post(
            'https://m.runoob.com/api/compile.php', data=data1, headers=headers)
        if len(r.text) > 3000:
            return "response too long,check your code!!"
        error = ''
        jsoncla = json.loads(r.text)
        if jsoncla.get('errors'):
            error = jsoncla['errors']
        if error == '\n':
            error = ''
        output = jsoncla['output']
        return str(output) + error