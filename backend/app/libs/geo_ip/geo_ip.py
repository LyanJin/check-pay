# https://github.com/maxmind/GeoIP2-python
# https://db-ip.com/db/download/ip-to-country-lite
import os

import geoip2.database


class GeoIpKit:
    PATH_MMDB = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(PATH_MMDB, 'dbip-country-lite-2019-09.mmdb')

    def __init__(self, ip):
        self.ip = ip

    @property
    def country(self):
        return geoip2.database.Reader(self.DB_PATH).country(self.ip).country

    @property
    def country_name(self):
        try:
            return self.country.names.get('zh-CN') or self.country.names.get('en')
        except:
            return self.ip

    @property
    def location(self):
        return self.country_name

    def is_ip_from_china(self):
        try:
            return self.country.name == 'China'
        except:
            return False


if __name__ == '__main__':
    for ip in ['127.0.0.1', '175.151.66.36', '110.54.205.237', '18.162.226.178', '220.134.110.231']:
        print('----------------------')
        print(ip)
        kit = GeoIpKit(ip)
        print(kit.is_ip_from_china())
        print(kit.country_name)
        print(kit.location)

