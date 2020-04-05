from werkzeug.routing import BaseConverter

from .views import *

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def add_routes(app, options):
    app.url_map.converters['regex'] = RegexConverter

    app.add_url_rule('/api/user', view_func=UserApi.as_view('user_api'))
    app.add_url_rule('/api/user/check', view_func=CheckUserApi.as_view('check_user_api'))
    app.add_url_rule('/api/user/logout', view_func=LogoutUserApi.as_view('logout_user_api'))
    app.add_url_rule('/api/games', view_func=ListGamesApi.as_view('list_games_api'))
    app.add_url_rule('/api/games/<int:game_pk>', view_func=GameDetailApi.as_view('game_detail_api'))
    app.add_url_rule('/api/tickets/<int:game_pk>', view_func=TicketsApi.as_view('list_tickets_api'))
    app.add_url_rule('/api/tickets/<int:game_pk>/<int:ticket_pk>', view_func=TicketsApi.as_view('get_ticket_api'))
    app.add_url_rule('/api/tickets/<int:game_pk>/<int:ticket_pk>/<int:number>', view_func=CheckCellApi.as_view('check_cell_api'))
    app.add_url_rule('/api/game/<int:game_pk>/get/ticket-<int:ticket_pk>.pdf',
                 view_func=DownloadTicketView.as_view('download_ticket_api'))

    if options.ui_version == 2:
        app.add_url_rule('/<regex("(css|img|fonts)"):folder>/<path:path>', view_func=ServeStaticFileView.as_view('static_files'))
        app.add_url_rule('/<path:path>', view_func=SpaIndexView.as_view('spa_index'))
        app.add_url_rule('/', view_func=SpaIndexView.as_view('index'))
    else:
        app.add_url_rule('/login', view_func=LoginView.as_view('login'))
        app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
        app.add_url_rule('/register', view_func=RegisterView.as_view('register'))
        app.add_url_rule('/game/<int:game_pk>', view_func=GameView.as_view('game'))
        app.add_url_rule('/game/<int:game_pk>/add/<int:ticket_pk>',
                        view_func=ChooseTicketView.as_view('add_ticket'))
        app.add_url_rule('/game/<int:game_pk>/get/<int:ticket_pk>',
                        view_func=DownloadTicketView.as_view('download_ticket'))
        app.add_url_rule('/play/<int:game_pk>',
                        view_func=TicketsView.as_view('view_tickets'))
        app.add_url_rule('/', view_func=IndexView.as_view('index'))
