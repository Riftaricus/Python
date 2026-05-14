import geocoder

def getLoc():
    g = geocoder.ip("me")
    
    return g.latlng
