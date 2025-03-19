class Context:
    '''
    Context class to store user's context information
    '''
    def __init__(self, user=None, travel_season=None, available_time=None, travel_companion=None, special_interests=None):
        self.user = user
        self.travel_season = travel_season
        self.available_time = available_time
        self.travel_companion = travel_companion
        self.special_interests = special_interests