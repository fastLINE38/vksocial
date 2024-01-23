#from ok_api import OkApi

class Socauth:
    tokenvk_def = 'vk1.a.eb0RJR2i0bHPrcSwApW6qcfbR5ThWjvtdDEQAvnyQAb8Vs-U5qLUr4lNf9n-vkRYKcr7_QojpWYrvpY4w8rVcjC5dMr8PoEPxdBnOuG1LZHZHPkI8q6NxsfA4jg9OL011cPN94f2v3slaNkqCfhSG1nnIftzImkV7vot0FyCEFTbiD3XLaqVTixwU1hlQnL7qlS5LtBHYhtq6T9gI5T_QA'

    '''
    def ok_authorization(self):
        self.ok_params = OkApi(access_token='tkn245q0yMdI1Dvv3uYj9KRLTMDYJ83ILHINzC6xf3VNPPVgdyL0O859dz8TcxssOmuFatoSpZTtJ9qRVNjyOC0',
               application_key='CBJJMHLGDIHBABABA',
               application_secret_key='A5FE87311D08DC889A37196B')
        return self.ok_params
    '''

    def set_vk_token(self, tok):
        self.tokenvk_def = tok

    def get_vk_token(self):
        return self.tokenvk_def
