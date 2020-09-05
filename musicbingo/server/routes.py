"""
Provides the URL routing for the views and REST API
"""

from werkzeug.routing import BaseConverter  # type: ignore

from .views import DownloadTicketView, ServeStaticFileView, SpaIndexView  # , LoginView, LogoutView
#from .views import RegisterView, GameView, ChooseTicketView, TicketsView, IndexView
from .api import (
    DatabaseApi, UserApi, CheckUserApi, ResetPasswordUserApi, UserManagmentApi,
    ListGamesApi, GameDetailApi, TicketsApi, TicketsStatusApi, CheckCellApi,
    RefreshApi, ModifyUserApi, GuestAccountApi, CreateGuestTokenApi,
    DeleteGuestTokenApi, ExportGameApi
)


class RegexConverter(BaseConverter):
    """
    Utility class to allow a regex to be used in a route path
    """
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]


def add_routes(app):
    """
    Install all routes into the app
    """
    app.url_map.converters['regex'] = RegexConverter

    app.add_url_rule('/api/refresh',
                     view_func=RefreshApi.as_view('refresh_api'))
    app.add_url_rule('/api/database',
                     view_func=DatabaseApi.as_view('database_api'))
    app.add_url_rule('/api/user',
                     view_func=UserApi.as_view('user_api'))
    app.add_url_rule('/api/user/check',
                     view_func=CheckUserApi.as_view('check_user_api'))
    # app.add_url_rule('/api/user/logout',
    #    view_func=LogoutUserApi.as_view('logout_user_api'))
    app.add_url_rule('/api/user/reset',
                     view_func=ResetPasswordUserApi.as_view('reset_password_user_api'))
    app.add_url_rule('/api/user/modify',
                     view_func=ModifyUserApi.as_view('modify_user_api'))
    app.add_url_rule('/api/user/guest',
                     view_func=GuestAccountApi.as_view('guest_user_api'))
    app.add_url_rule('/api/user/guest/add',
                     view_func=CreateGuestTokenApi.as_view('create_guest_user_api'))
    app.add_url_rule('/api/user/guest/delete/<path:token>',
                     view_func=DeleteGuestTokenApi.as_view('delete_guest_token_api'))
    app.add_url_rule('/api/users',
                     view_func=UserManagmentApi.as_view('user_managment_api'))
    app.add_url_rule('/api/games',
                     view_func=ListGamesApi.as_view('list_games_api'))

    app.add_url_rule('/api/game/<int:game_pk>/tickets',
                     view_func=TicketsApi.as_view('list_tickets_api'))

    app.add_url_rule('/api/game/<int:game_pk>',
                     view_func=GameDetailApi.as_view('game_detail_api'))
    app.add_url_rule('/api/game/<int:game_pk>/export',
                     view_func=ExportGameApi.as_view('game_export_api'))
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
    app.add_url_rule(r'/<regex("(favicon.*|.*\.(gif|png)|.*\.js(on)?)"):path>',
                     view_func=ServeStaticFileView.as_view('root_static_files'))
    app.add_url_rule('/user/reset/<path:path>', view_func=SpaIndexView.as_view('reset_password'))
    app.add_url_rule('/<path:path>', view_func=SpaIndexView.as_view('spa_index'))
    app.add_url_rule('/', view_func=SpaIndexView.as_view('index'))
