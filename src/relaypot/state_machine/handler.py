class Handler():
    class node():

        def __init__(self, pre, post):
            self.pre = [pre]
            self.post = []
        def attach(self, post):
            self.pre.append(post)
            post.pre
    
    def __init__(self):
        self

    def add_