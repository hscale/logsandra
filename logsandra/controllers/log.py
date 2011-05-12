import datetime

from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import redirect

from logsandra.lib.base import BaseController, render
from logsandra.model.client import CassandraClient

class LogController(BaseController):

    def index(self):
        return render('/log_index.html')

    def parse_datestr(self, datestr):
        if not datestr:
            return ''
        try:
            d = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            redirect(url(controller='log', action='error'))
        return d

    def view(self):
        date_from = request.GET['date_from']
        date_to = request.GET['date_to']
        status = request.GET['status']
        search_keyword = request.GET['search_keyword']

        if search_keyword:
            keyword = search_keyword
        else:
            keyword = status

        current_prev = current_next = None
        if 'next' in request.GET:
            n = request.GET['next']
            if n is not None:
                current_next = long(n)

        if 'prev' in request.GET:
            p = request.GET['prev']
            if p is not None:
                current_prev = long(p)

        date_from = self.parse_datestr(date_from)
        date_to = self.parse_datestr(date_to)

        client = CassandraClient(config['ident'], config['cassandra_host'],
                                 config['cassandra_port'], config['cassandra_timeout'])
        kwargs = {}
        if current_next:
            kwargs = {'action_next': current_next}
        elif current_prev:
            kwargs = {'action_prev': current_prev}

        entries, prev, next = client.get_by_keyword(
            keyword, date_from, date_to, **kwargs)

        c.entries = entries

        if prev:
            c.prev_url = url(controller='log', action='view',
                    search_keyword=request.GET['search_keyword'],
                    status=request.GET['status'],
                    date_from=request.GET['date_from'],
                    date_to=request.GET['date_to'], prev=prev)

        if next:
            c.next_url = url(controller='log', action='view',
                    search_keyword=request.GET['search_keyword'],
                    status=request.GET['status'],
                    date_from=request.GET['date_from'],
                    date_to=request.GET['date_to'], next=next)

        return render('/log_view.html')

    def error(self):
        return 'Error, could not parse date'
