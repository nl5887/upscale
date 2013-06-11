def application(environ, start_response):
    status = '200 OK'

    headers = [
        ('Content-Type', 'text/html')
    ]

    start_response(status, headers)
    yield "<p>Hello"
    yield "World</p>"

from gevent.pywsgi import WSGIServer

p = WSGIServer(('', 8000), application)
#p.serve_forever()
print p

