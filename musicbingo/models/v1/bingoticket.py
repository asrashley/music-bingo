from random import shuffle
import typing

from pony.orm import PrimaryKey, Required, Optional, Set, Json # type: ignore
from pony.orm import composite_key, flush # type: ignore

from musicbingo.models.db import db, schema_version

from .user import User

class BingoTicket(db.Entity): # type: ignore
    __plural__ = 'BingoTickets'

    pk = PrimaryKey(int, auto=True)
    user = Optional(User)
    game = Required('Game')
    number = Required(int, unsigned=True)
    tracks = Set('Track')
    fingerprint = Required(str)  # calculated by multiplying the primes of each track on this ticket
    order = Optional(Json) # List[int] - order of tracks by pk
    checked = Optional(int, size=64, default=0) # bitmask of track order
    composite_key(game, number)

    def tracks_in_order(self) -> typing.List["Track"]:
        """
        Get the list of tracks, in the order they appear on the ticket
        """
        #if not self.order:
        #    self.order = list(select(track.pk for track in self.tracks).random(len(self.tracks)))
        tk_map = {}
        for trck in self.tracks:
            tk_map[trck.pk] = trck
            if self.order and trck.pk not in self.order:
                self.order.append(trck.pk)
        if not self.order:
            order = list(tk_map.keys())
            shuffle(order)
            self.order = order
        elif None in self.order:
            # work-around for bug that did not wait for Track.pk to be
            # calculated when generating order
            self.order = list(filter(lambda item: item is not None, self.order))
        tracks: typing.List[Track] = []
        for tpk in self.order:
            if tpk in tk_map:
                tracks.append(tk_map[tpk])
        return tracks

    @classmethod
    def import_json(cls, items, options,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> None:
        if schema_version == 1:
            from musicbingo.models.v1.schema import Game, Track
        else:
            from musicbingo.models.v2.schema import Game, Track

        pk_map: typing.Dict[int, int] = {}
        pk_maps[cls] = pk_map
        for item in items:
            try:
                ticket = BingoTicket.get(pk=item['pk'])
            except KeyError:
                ticket = None
            game = Game.get(pk=item['game'])
            if not game:
                print('Warning: failed to find game {game} for ticket {pk}'.format(**item))
                continue
            user = None
            if item['user']:
                user = User.get(pk=item['user'])
                if not user:
                    print('Warning: failed to find user {user} for ticket {pk} in game {game}'.format(**item))
            tracks = []
            # The database field "order" has the list of Track primary keys.
            # The JSON representation of BingoTicket should have a property called
            # "tracks" which is an ordered list of Track.pk. If the JSON
            # file has an "order" property, it can be used as a fallback.
            if 'order' in item and 'tracks' not in item:
                item['tracks'] = item['order']
            for trk in item['tracks']:
                track = Track.get(pk=trk)
                if track is None and trk in pk_maps[Track]:
                    track = Track.get(pk=pk_maps[Track][trk])
                if not track:
                    print('Warning: failed to find track {trk} for ticket {pk} in game {game}'.format(trk=trk, **item))
                else:
                    tracks.append(track)
            item['game'] = game
            item['user'] = user
            item['tracks'] = tracks
            if 'order' not in item:
                item['order'] = [t.pk for t in item['tracks']]
            if ticket is None:
                ticket = BingoTicket(**item)
            else:
                for key, value in item.items():
                    if key not in ['pk']:
                        setattr(ticket, key, value)
            flush()
            pk_map[item['pk']] = ticket.pk
