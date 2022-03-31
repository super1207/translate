import js2py
import requests
from urllib import parse
import re
import time
class baidu:
    '''用于百度翻译
    '''
    def __init__(self):
        self.bd_js_code = r'''function a(r) { if (Array.isArray(r)) { for (var o = 0, t = Array(r.length); o < 
        r.length; o++) t[o] = r[o]; return t } return Array.from(r) } function n(r, o) { for (var t = 0; t < o.length 
        - 2; t += 3) { var a = o.charAt(t + 2); a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a), a = "+" === 
        o.charAt(t + 1) ? r >>> a : r << a, r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a } return r } 
        function e(r) { var o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g); if (null === o) { var t = r.length; t > 
        30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10)) } else { for (var 
        e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), C = 0, h = e.length, f = []; h > C; C++) "" !== e[C] && 
        f.push.apply(f, a(e[C].split(""))), C !== h - 1 && f.push(o[C]); var g = f.length; g > 30 && (r = f.slice(0, 
        10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join("")) } var 
        u = void 0 , l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107); u = 
        null !== i ? i : (i = window[l] || "") || ""; for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[
        1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) { var A = r.charCodeAt(v); 128 > A ? S[c++] = A : (2048 > 
        A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 
        1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)), S[c++] = A >> 18 | 240, S[c++] = A >> 12 
        & 63 | 128) : S[c++] = A >> 12 | 224, S[c++] = A >> 6 & 63 | 128), S[c++] = 63 & A | 128) } for (var p = m, 
        F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + 
        String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(
        43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + 
        String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) 
        + String.fromCharCode(102)), b = 0; b < S.length; b++) p += S[b], p = n(p, F); return p = n(p, D), p ^= s, 
        0 > p && (p = (2147483647 & p) + 2147483648), p %= 1e6, p.toString() + "." + (p ^ m) } '''
        self.session = requests.Session()
        self.session.cookies.set(
            'BAIDUID', '19288887A223954909730262637D1DEB:FG=1;')
        self.session.cookies.set('PSTM', '%d;' % int(time.time()))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/62.0.3202.94 Safari/537.36 '
        }
        self.data = {
            'query': '',
            'simple_means_flag': '3',
            'sign': '',
            'token': '',
        }
        self.url = 'https://fanyi.baidu.com/v2transapi'

    def translate(self, word, to):
        if to == 'zh-CN':
            to = 'zh'
        elif to == 'zh-TW':
            to = 'cht'
        elif to == 'ja':
            to = 'jp'
        elif to == 'ko':
            to = 'kor'
        self.data['query'] = word
        self.data['from'] = 'auto'
        if self.data['from'] == to:
            return word
        self.data['to'] = to
        self.data['token'], gtk = self.getTokenGtk()
        self.data['token'] = '6482f137ca44f07742b2677f5ffd39e1'
        self.data['sign'] = self.getSign(gtk, word)
        res = self.session.post(self.url, data=self.data, headers=self.headers, verify=False)
        # print(res.json())
        out = res.json()['trans_result']['data']
        return '\n'.join([x['dst'] for x in out])

    def langdetect(self, word):
        self.data['query'] = word[:49]
        res = self.session.post('https://fanyi.baidu.com/langdetect', data=self.data, verify=False)
        # print(res.json())
        return res.json()['lan']

    def getTokenGtk(self):
        url = 'https://fanyi.baidu.com/'
        res = requests.get(url, headers=self.headers, verify=False)
        token = re.findall(r"token: '(.*?)'", res.text)[0]
        gtk = re.findall(r";window.gtk = ('.*?');", res.text)[0]
        return token, gtk

    def getSign(self, gtk, word):
        evaljs = js2py.EvalJs()
        js_code = self.bd_js_code
        js_code = js_code.replace(
            'null !== i ? i : (i = window[l] || "") || ""', gtk)
        evaljs.execute(js_code)
        sign = evaljs.e(word)
        return sign
