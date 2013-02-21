from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip
from django.core.management.base import BaseCommand, CommandError
import ujson

from pyshort.strings import gunzip
from uploadapi.models import File

TEMPLATE_DOCUMENT = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>YouSense</name>
    <description>YouSense user paths</description>
    {styles}
    {paths}
  </Document>
</kml>
"""

TEMPLATE_STYLE = """    <Style id="style-{installid}">
      <LineStyle>
        <color>ff{color}</color>
        <width>4</width>
      </LineStyle>
    </Style>
"""

TEMPLATE_PATH = """    <Placemark>
      <name>{installid}</name>
      <styleUrl>#style-{installid}</styleUrl>
      <LineString>
        <tessellate>1</tessellate>
        <altitudeMode>clampToGround</altitudeMode>
        <coordinates>
        {coords}
        </coordinates>
      </LineString>
    </Placemark>
"""

TEMPLATE_COORD = '{lng},{lat},{altitude}'

COLORS = ['ffff00', 'ff0000', '00ff00', '0000ff', '00ffff']

class Command(BaseCommand):
    help = 'Exports all GPS paths in Google Earth .kml format.'

    def handle(self, *args, **options):
        installids = set(File.objects.values_list('installid', flat=True).distinct())
        styles = [TEMPLATE_STYLE.format(installid=installid, color=COLORS[i]) for (i, installid) in enumerate(installids)]
        paths = []
        for installid in installids:
            gps = self.user_gps(installid)
            coords = [TEMPLATE_COORD.format(**event) for event in gps]
            paths.append(TEMPLATE_PATH.format(installid=installid, coords='\n'.join(coords)))
        self.stdout.write(TEMPLATE_DOCUMENT.format(styles=''.join(styles), paths=''.join(paths)))

    def user_gps(self, installid):
        gps = []
        for ufile in File.objects.filter(installid=installid):
            for event in self.file_events(ufile):
                if event['tag'] == 'sensor.gps':
                    gps.append(event['data'])
        gps.sort(key=lambda d: d['time'])
        return gps

    def file_events(self, ufile):
        for jsonevent in gunzip(ufile.body).split('\0'):
            jsonevent = jsonevent.strip()
            if jsonevent:
                yield ujson.loads(jsonevent)

