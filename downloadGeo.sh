curl -O geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz 
curl -O geolite.maxmind.com/download/geoip/database/GeoLite2-Country.mmdb.gz 
gunzip -c GeoLite2-City.mmdb.gz > _private/GeoLite2-City.mmdb
gunzip -c GeoLite2-Country.mmdb.gz > _private/GeoLite2-Country.mmdb
rm GeoLite2*

