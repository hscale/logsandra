import logging

from pylons import request, response, session, tmpl_context as c, url, config
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from logsandra.lib.base import BaseController, render
from logsandra.model.client import CassandraClient

log = logging.getLogger(__name__)

class GraphController(BaseController):

    def index(self):
        return render('/graph_index.html')

    def view(self):
        c.keyword = request.GET['keyword']
        return render('/graph_view.html')

    @jsonify
    def ajax(self):
        client = CassandraClient(config['ident'], config['cassandra_host'], config['cassandra_port'], config['cassandra_timeout'])
        keyword = request.GET['keyword']
        end_date = ''
        if 'next' in request.GET and request.GET['next']
            end_date = long(request.GET['next'])

        return {'result': client.get_date_count(keyword, end_date=end_date, count=250)}

    def error(self):
        return 'Error, could not parse date'
