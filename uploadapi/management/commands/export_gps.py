from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip
from collections import defaultdict
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

TEMPLATE_STYLE = """    <Style id="style-{imei}">
      <LineStyle>
        <color>ff{color}</color>
        <width>4</width>
      </LineStyle>
    </Style>
"""

TEMPLATE_PATH = """    <Placemark>
      <name>{imei}</name>
      <styleUrl>#style-{imei}</styleUrl>
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
        imeifixes = sorted(self.sorted_fixes_by_imei().iteritems())
        styles = [TEMPLATE_STYLE.format(imei=imei, color=COLORS[i]) for (i, (imei, fixes)) in enumerate(imeifixes)]
        paths = []
        for imei, fixes in imeifixes:
            coords = [TEMPLATE_COORD.format(**gps) for gps in fixes]
            paths.append(TEMPLATE_PATH.format(imei=imei, coords='\n'.join(coords)))
        self.stdout.write(TEMPLATE_DOCUMENT.format(styles=''.join(styles), paths=''.join(paths)))

    def sorted_fixes_by_imei(self):
        imeis, userfixes = self.data_maps()
        imeifixes = defaultdict(list)
        for userid, fixes in userfixes.iteritems():
            assert userid in imeis
            imeifixes[imeis[userid]].extend(fixes)
        for imei, fixes in imeifixes.iteritems():
            fixes.sort(key=lambda d: d['time'])
        return imeifixes

    def data_maps(self):
        """Returns two dictionaries: userid->IMEI and userid->unsorted GPS fixes."""
        imeis = {}
        fixes = defaultdict(list)

        for ufile in File.objects.all():
            for header, event in self.file_events(ufile):
                if event['tag'] == 'device.telephony':
                    imeis[header['data']['userid']] = event['data']['device_id']
                elif event['tag'] == 'sensor.gps':
                    fixes[header['data']['userid']].append(event['data'])
        return imeis, fixes

    def file_events(self, ufile):
        header = None
        for jsonevent in gunzip(ufile.body).split('\0'):
            jsonevent = jsonevent.strip()
            if jsonevent:
                event = ujson.loads(jsonevent)
                if header is None:
                    assert event['tag'] == 'header'  # First event must be header.
                    header = event
                else:
                    assert event['tag'] != 'header'  # Only one header allowed.
                    yield header, event

