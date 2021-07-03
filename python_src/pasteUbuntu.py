import requests
import random
class pasteUbuntu:
    '''用于向paste.ubuntu.com发送数据，获取临时链接
    '''
    def translate(self, word, to, poster='anonymous', syntax='text', expiration=''):
        """POST something to " http://paste.ubuntu.com/ "

        Args:
            content: Something you want to post.
            poster: Your name.
            syntax: The programming language you use.
            expiration: The time you want to save.

        Returns:
            A string represents a website.
        """
        Guid = '.'.join([''.join([random.choice('0123456789')
                                for k in range(i)]) for i in [8, 19, 13, 4]])
        header = {
            "Host": "paste.ubuntu.com"
        }
        data = {
            "poster": poster,
            "syntax": syntax,
            "expiration": expiration,
            "content": word
        }
        cookies = {
            '__guid': Guid
        }
        r = requests.post('http://paste.ubuntu.com/', cookies=cookies,
                        headers=header, data=data, verify=False, allow_redirects=False)
        return "https://paste.ubuntu.com" + r.headers['Location']
