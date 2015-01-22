#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2014/9/12

from gevent.wsgi import WSGIServer
from monitor import app
http_server = WSGIServer(('', 80), app)
http_server.serve_forever()
