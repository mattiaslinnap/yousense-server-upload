"""Helpers for generating Google Earth files from GPS data."""

from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip
import colorsys
from cStringIO import StringIO
import random
import zipfile

from pyshort.iterables import igrouper

TEMPLATE_DOCUMENT = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>YouSense</name>
    <description>YouSense user paths</description>
    {styles}
    {placemarks}
  </Document>
</kml>
"""


TEMPLATE_STYLE = """    <Style id="style-{name}">
      <LineStyle>
        <color>{color}</color>
        <width>4</width>
      </LineStyle>
    </Style>
"""


TEMPLATE_PLACEMARK = """    <Placemark>
      <name>{name}</name>
      <styleUrl>#style-{name}</styleUrl>
      <MultiGeometry>
        {linestrings}
      </MultiGeometry>
    </Placemark>
"""

TEMPLATE_LINESTRING = """   <LineString>
        <tessellate>1</tessellate>
        <altitudeMode>clampToGround</altitudeMode>
        <coordinates>
        {coords}
        </coordinates>
      </LineString>
"""

TEMPLATE_COORD = '          {lng:.5f},{lat:.5f},{altitude:.1f}'


def randomcolor():
    """Returns a probably unique ARGB color."""
    def hex(flt):
        return '{:02x}'.format(int(flt * 255))
    a = 0.8
    r, g, b = colorsys.hsv_to_rgb(random.random(), 1, 1)
    return ''.join(hex(f) for f in [a, r, g, b])


def kml(paths):
    """Returns a string with the Google Earth .kml format data for the paths.

    Paths must be a dictionary of name -> path pairs, where each path is a list of positions.
    Each position must have attributes lat, lng, and altitude.
    Name should be sensible and not contain XML characters.
    """
    names = sorted(paths)
    styles = [TEMPLATE_STYLE.format(name=name, color=randomcolor()) for (i, name) in enumerate(names)]
    placemarks = []
    for name in names:
        linestrings = []
        for linefixes in igrouper(paths[name], 10000):
            coords = [TEMPLATE_COORD.format(**fix) for fix in linefixes]
            linestrings.append(TEMPLATE_LINESTRING.format(coords='\n'.join(coords)))
        placemarks.append(TEMPLATE_PLACEMARK.format(name=name, linestrings='\n'.join(linestrings)))
    return TEMPLATE_DOCUMENT.format(styles=''.join(styles), placemarks=''.join(placemarks))


def kmz(paths):
    """Same as kml(paths), but returns a byte string with the contents of a Google Earth .kmz file.

    .kmz files are really .zip files with a single .kml file in them.
    """
    buf = StringIO()
    with zipfile.ZipFile(buf, 'w') as zfile:
        zfile.writestr('yousense.kml', kml(paths).encode('utf-8'), zipfile.ZIP_DEFLATED)
    return buf.getvalue()
