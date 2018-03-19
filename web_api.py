import cherrypy
import redis


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


cherrypy.quickstart(BSEData())
