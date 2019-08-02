import js2py
import requests
from urllib import parse
class google:
    '''用于谷歌翻译
    '''
    def __init__(self):
        self.gg_js_code = '''function TL(a){var k="";var b=406644;var b1=3293161072;var jd=".";var $b="+-a^+6";var 
        Zb="+-3^+b+-f";for(var e=[],f=0,g=0;g<a.length;g++){var m=a.charCodeAt(g);128>m?e[f++]=m:(2048>m?e[
        f++]=m>>6|192:(55296==(m&64512)&&g+1<a.length&&56320==(a.charCodeAt(g+1)&64512)?(m=65536+((m&1023)<<10)+(
        a.charCodeAt(++g)&1023),e[f++]=m>>18|240,e[f++]=m>>12&63|128):e[f++]=m>>12|224,e[f++]=m>>6&63|128),
        e[f++]=m&63|128)}a=b;for(f=0;f<e.length;f++){a+=e[f],a=RL(a,$b)}a=RL(a,Zb);a^=b1||0;0>a&&(a=(
        a&2147483647)+2147483648);a%=1000000;return a.toString()+jd+(a^b)}function RL(a,b){var t="a";var Yb="+";for(
        var c=0;c<b.length-2;c+=3){var d=b.charAt(c+2),d=d>=t?d.charCodeAt(0)-87:Number(d),d=b.charAt(
        c+1)==Yb?a>>>d:a<<d;a=b.charAt(c)==Yb?a+d&4294967295:a^d}return a}; '''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.102 Safari/537.36',
        }
        self.url = 'https://translate.google.cn/translate' \
                   '_a/single?client=webapp&sl=auto&tl={}&hl=zh-CN&' \
                   'dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=' \
                   'rm&dt=ss&dt=t&pc=1&otf=1&ssel=3&tsel=6&kc=1&tk={}&q={}'

    def translate(self, word, tl):
        if len(word) > 4891:
            raise RuntimeError(
                'The length of word should be less than 4891...')
        t = self.url.format(tl, self.getTk(word), parse.quote(word))
        # print(t)
        res = requests.get(t, headers=self.headers, verify=False)
        # print(res.content.decode('utf-8'))
        oo = res.json()[0]
        return ''.join([i[0] for i in oo[:len(oo) - 1]])

    def getTk(self, word):
        evaljs = js2py.EvalJs()
        js_code = self.gg_js_code
        evaljs.execute(js_code)
        tk = evaljs.TL(word)
        return tk