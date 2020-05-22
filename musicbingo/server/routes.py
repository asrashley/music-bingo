from werkzeug.routing import BaseConverter  # type: ignore

from .views import DownloadTicketView, ServeStaticFileView, SpaIndexView  # , LoginView, LogoutView
#from .views import RegisterView, GameView, ChooseTicketView, TicketsView, IndexView
from .api import (
    UserApi, CheckUserApi, ResetPasswordUserApi, UserManagmentApi,
    ListGamesApi, GameDetailApi, TicketsApi, TicketsStatusApi, CheckCellApi,
    RefreshApi
)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def add_routes(app):
    app.url_map.converters['regex'] = RegexConverter

    app.add_url_rule('/api/refresh',
                     view_func=RefreshApi.as_view('refresh_api'))
    app.add_url_rule('/api/user',
                     view_func=UserApi.as_view('user_api'))
    app.add_url_rule('/api/user/check',
                     view_func=CheckUserApi.as_view('check_user_api'))
    # app.add_url_rule('/api/user/logout',
    #    view_func=LogoutUserApi.as_view('logout_user_api'))
    app.add_url_rule('/api/user/reset',
                     view_func=ResetPasswordUserApi.as_view('reset_password_user_api'))
    app.add_url_rule('/api/users',
                     view_func=UserManagmentApi.as_view('user_managment_api'))
    app.add_url_rule('/api/games',
                     view_func=ListGamesApi.as_view('list_games_api'))

    app.add_url_rule('/api/game/<int:game_pk>/tickets',
                     view_func=TicketsApi.as_view('list_tickets_api'))

    app.add_url_rule('/api/game/<int:game_pk>',
                     view_func=GameDetailApi.as_view('game_detail_api'))

    app.add_url_rule('/api/game/<int:game_pk>/status',
                     view_func=TicketsStatusApi.as_view('tickets_status_api'))
    app.add_url_rule('/api/game/<int:game_pk>/ticket/<int:ticket_pk>',
                     view_func=TicketsApi.as_view('get_ticket_api'))
    app.add_url_rule('/api/game/<int:game_pk>/ticket/<int:ticket_pk>/cell/<int:number>',
                     view_func=CheckCellApi.as_view('check_cell_api'))
    app.add_url_rule('/api/game/<int:game_pk>/ticket/ticket-<int:ticket_pk>.pdf',
                     view_func=DownloadTicketView.as_view('download_ticket_api'))

    app.add_url_rule('/<regex("(css|img|fonts)"):folder>/<path:path>',
                     view_func=ServeStaticFileView.as_view('static_files'))
    app.add_url_rule('/<regex("(favicon.*|.*\.(gif|png)|.*\.js(on)?)"):path>',
                     view_func=ServeStaticFileView.as_view('root_static_files'))
    app.add_url_rule('/user/reset/<path:path>', view_func=SpaIndexView.as_view('reset_password'))
    app.add_url_rule('/<path:path>', view_func=SpaIndexView.as_view('spa_index'))
    app.add_url_rule('/', view_func=SpaIndexView.as_view('index'))
