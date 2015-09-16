import tornado.ioloop

from corpsearch import app

if __name__ == '__main__':
    app.listen(2020)
    tornado.ioloop.IOLoop.current().start()
