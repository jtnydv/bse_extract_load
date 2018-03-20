import cherrypy
import redis
import os


class BSEData(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        conn = redis.Redis(host='redis-10041.c8.us-east-1-4.ec2.cloud.redislabs.com', port=10041, db=0, password='6relaA2NNReIr7ZseaDPTeQArzcjlaDX')
        data = conn.hgetall('bse_data')
        return list(data.itervalues())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search(self, keyword):
        conn = redis.Redis(host='redis-10041.c8.us-east-1-4.ec2.cloud.redislabs.com', port=10041, db=0, password='6relaA2NNReIr7ZseaDPTeQArzcjlaDX')
        search_str = '*' + keyword + '*'
        response = []
        for key, data in conn.hscan_iter('bse_data', match=search_str):
            response.append(data)
        return response


config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000)),
    }
}

cherrypy.quickstart(BSEData(), '/', config=config)
