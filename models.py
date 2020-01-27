"""
Findpairs tables Mock
"""
class User:
    pass

class Online:
    pass

def generate_id():
    id = 0
    while True:
        id += 1
        yield id

GAME_ID = generate_id()

class Game:
    def __init__(self, **kwargs):
        self.gameId = next(GAME_ID)
        self.numPlayers = kwargs['numPlayers']
        self.numPairs = kwargs['numPairs']
        self.creator = kwargs['creator']
        self.state = ''

    def __str__(self):
        return "gameId=" + str(self.gameId) +\
            ', numPlayers=' + str(self.numPlayers) +\
            ', numPairs=' + str(self.numPairs)

MATCH_COL_USER = 2
MATCH_COL_NUMPLAYER = 3

class Objects:
    def __init__(self, **kwargs):
        self.values = []
        self.filter_game_id = False
        self.filter_user = False
        self.game_id = 0
        self.user = ''

    def filter(self, **kwargs):
        if 'game_id' in kwargs:
            self.filter_game_id = True
            self.game_id = kwargs['game_id']
        else:
            self.filter_game_id = False

        if 'user' in kwargs:
            self.filter_user = True
            self.user = kwargs['user']
        else:
            self.filter_user = False
    
        return self

    def values_list(self, **kwargs):
        values = []
        values_filtered_by_game_id = []

        if self.filter_game_id:
            for value in self.values:
                if value[1] == self.game_id:
                    values_filtered_by_game_id.append(value)
        else:
            values_filtered_by_game_id = self.values.copy()

        if self.filter_user:
            for value in values_filtered_by_game_id:
                if value[MATCH_COL_USER] == self.user:
                    values.append(value)
        else:
            values = values_filtered_by_game_id.copy()

        return values # [(0, 1, "Veera", 0), (0, 1, "Helmi", 1)]

    def insert(self, val):
        self.values.append(val)

    def remove_all(self):
        self.values.clear()

class DoesNotExist(Exception):
    pass

class Match:
    objects = Objects()
    DoesNotExist = DoesNotExist()

    @staticmethod
    def save(match):
        Match.objects.insert(match)

    @staticmethod
    def remove_all():
        Match.objects.remove_all()
