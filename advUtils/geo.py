import typing as _t
import types as _tp
import requests

from advUtils.core.decorators import on_define, ExperimentalWarning

try:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from geopy import Location
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from geopy.geocoders import Nominatim, GeoNames
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from geopy.distance import Geodesic
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import geocoder
except ImportError:
    Location: _t.Optional[_t.Callable] = None
    Nominatim: _t.Optional[_t.Callable] = None
    GeoNames: _t.Optional[_t.Callable] = None
    Geodesic: _t.Optional[_t.Callable] = None
    geocoder: _t.Optional[_tp.ModuleType] = None


@on_define()
def main():
    import warnings
    import os
    warnings.warn(
        "Call to experimental file '%s'" % os.path.relpath(__file__), category=ExperimentalWarning, stacklevel=3)


geolocator = Nominatim(user_agent="QTestingService")
location: Location = geolocator.geocode("Radioweg 45, Almere")
location2: Location = geolocator.geocode("Vrouwenakker 12a, Vrouwenakker, Nederland")
# noinspection PyUnresolvedReferences
print(location.address)
# noinspection PyUnresolvedReferences
print(location.raw)
# noinspection PyUnresolvedReferences
print(location.latitude, location.longitude)

send_url = 'http://ipinfo.io/loc'
r = requests.get(send_url)
loc = r.text
print(loc)

location: Location = geolocator.reverse(f"{loc}")
# noinspection PyUnresolvedReferences
print(location.address)

# noinspection PyUnresolvedReferences
g = geocoder.ip('me')
print(f"{g.latlng[0]},{g.latlng[1]}")
# print(g.latlng)

location: Location = geolocator.reverse(f"{g.latlng[0]},{g.latlng[1]}")
# noinspection PyUnresolvedReferences
print(location.address)


def display_ip():
    """  Function To Print GeoIP Latitude & Longitude """
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    geo_request = requests.get('https://get.geojs.io/v1/ip/geo/' + my_ip + '.json')
    geo_data = geo_request.json()
    # print({'latitude': geo_data['latitude'], 'longitude': geo_data['longitude']})
    lat2 = geo_data['latitude']
    lon2 = geo_data['longitude']
    print(f"{lat2},{lon2}")

    location_: Location = geolocator.reverse(f"{lat2},{lon2}")
    # noinspection PyUnresolvedReferences
    print(location_.address)


display_ip()
