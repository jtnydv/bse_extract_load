import cherrypy
import redis
import os


class BSEData(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        conn = redis.Redis('localhost')
        data = conn.hgetall('bse_data')
        return list(data.itervalues())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search(self, keyword):
        conn = redis.Redis('localhost')
        search_str = '*' + keyword + '*'
        response = []
        for key, data in conn.hscan_iter('bse_data', match=search_str):
            response.append(data)
        return response

cherrypy.config.update({'server.socket_host': '0.0.0.0',})
cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')),})
cherrypy.quickstart(BSEData())
