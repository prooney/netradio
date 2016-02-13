

mockstations = [{ 'name': 'Seymour FM 103.9', 'id': 1, 'streams' : ['http://groove.wavestreamer.com:5890/Live']}, 
           { 'name': 'Triple J NSW', 'id': 2, 'streams' : ['http://live-radio01.mediahubaustralia.com/2TJW/mp3/', 'http://live-radio02.mediahubaustralia.com/2TJW/mp3/']},
           { 'name': 'ABC Melbourne', 'id': 3, 'streams' : ['http://live-radio01.mediahubaustralia.com/3LRW/mp3/', 'http://live-radio01.mediahubaustralia.com/2TJW/mp3/']}
           ]

class MockStationDB(object):
    def __init__(self, dburl):
        self.stations = mockstations

    def search(self, searchstr=None):

        if searchstr == None:
            result = self.stations
        else:
            result = [station for station in self.stations if searchstr.lower() in station['name'].lower()]
        print(result)
        return result


class StationDB(object):
    def __init__(self, dburl):
        pass
    def search(self, searchstr):
        return []
