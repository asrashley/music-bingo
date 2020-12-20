"""
Provides the URL routing for the views and REST API
"""

from flask import request  # type: ignore
from werkzeug.routing import BaseConverter  # type: ignore

from . import api
from . import views

class RegexConverter(BaseConverter):
    """
    Utility class to allow a regex to be used in a route path
    """
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]

def no_api_cache(response):
    """
    Make sure all API calls return no caching directives
    """
    if request.path.startswith('/api/'):
        response.cache_control.max_age = 0
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
    return response


def add_routes(app):
    """
    Install all routes into the app
    """
    app.url_map.converters['regex'] = RegexConverter

    app.after_request(no_api_cache)

    app.add_url_rule('/api/refresh',
                     view_func=api.RefreshApi.as_view('refresh_api'))
    app.add_url_rule('/api/database',
                     view_func=api.DatabaseApi.as_view('database_api'))
    app.add_url_rule('/api/directory',
                     view_func=api.ListDirectoryApi.as_view('directory_index_api'))
    app.add_url_rule('/api/directory/<int:dir_pk>',
                     view_func=api.DirectoryDetailsApi.as_view('directory_details_api'))
    app.add_url_rule('/api/user',
                     view_func=api.UserApi.as_view('user_api'))
    app.add_url_rule('/api/user/check',
                     view_func=api.CheckUserApi.as_view('check_user_api'))
    # app.add_url_rule('/api/user/logout',
    #    view_func=LogoutUserApi.as_view('logout_user_api'))
    app.add_url_rule('/api/user/reset',
                     view_func=api.ResetPasswordUserApi.as_view('reset_password_user_api'))
    app.add_url_rule('/api/user/modify',
                     view_func=api.ModifyUserApi.as_view('modify_user_api'))
    app.add_url_rule('/api/user/guest',
                     view_func=api.GuestAccountApi.as_view('guest_user_api'))
    app.add_url_rule('/api/user/guest/add',
                     view_func=api.CreateGuestTokenApi.as_view('create_guest_user_api'))
    app.add_url_rule('/api/user/guest/delete/<path:token>',
                     view_func=api.DeleteGuestTokenApi.as_view('delete_guest_token_api'))
    app.add_url_rule('/api/users',
                     view_func=api.UserManagmentApi.as_view('user_managment_api'))
    app.add_url_rule('/api/games',
                     view_func=api.ListGamesApi.as_view('list_games_api'))

    app.add_url_rule('/api/game/<int:game_pk>/tickets',
                     view_func=api.TicketsApi.as_view('list_tickets_api'))

    app.add_url_rule('/api/game/<int:game_pk>',
                     view_func=api.GameDetailApi.as_view('game_detail_api'))
    app.add_url_rule('/api/game/<int:game_pk>/export',
                     view_func=api.ExportGameApi.as_view('game_export_api'))
    app.add_url_rule('/api/game/<int:game_pk>/status',
                     view_func=api.TicketsStatusApi.as_view('tickets_status_api'))
    app.add_url_rule('/api/game/<int:game_pk>/ticket/<int:ticket_pk>',
                     view_func=api.TicketsApi.as_view('get_ticket_api'))
    app.add_url_rule('/api/game/<int:game_pk>/ticket/<int:ticket_pk>/cell/<int:number>',
                     view_func=api.CheckCellApi.as_view('check_cell_api'))
    app.add_url_rule('/api/game/<int:game_pk>/ticket/ticket-<int:ticket_pk>.pdf',
                     view_func=views.DownloadTicketView.as_view('download_ticket_api'))
    app.add_url_rule('/api/song/<int:dir_pk>',
                     view_func=api.SongApi.as_view('directory_query_api'))
    app.add_url_rule('/api/song',
                     view_func=api.SongApi.as_view('song_query_api'))

    app.add_url_rule('/<regex("(css|img|fonts)"):folder>/<path:path>',
                     view_func=views.ServeStaticFileView.as_view('static_files'))
    app.add_url_rule(r'/<regex("(favicon.*|.*\.(gif|png)|.*\.js(on)?)"):path>',
                     view_func=views.ServeStaticFileView.as_view('root_static_files'))
    app.add_url_rule('/user/reset/<path:path>',
                     view_func=views.SpaIndexView.as_view('reset_password'))
    app.add_url_rule('/<path:path>', view_func=views.SpaIndexView.as_view('spa_index'))
    app.add_url_rule('/', view_func=views.SpaIndexView.as_view('index'))
