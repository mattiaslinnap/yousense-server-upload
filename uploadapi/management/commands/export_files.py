from __future__ import absolute_import, division, print_function, unicode_literals
from future_builtins import *  # ascii, filter, hex, map, oct, zip
from django.core.management.base import BaseCommand, CommandError
import os
import re

from uploadapi.models import File


class Command(BaseCommand):
    args = '<output directory>'
    help = 'Exports all uploaded files to a directory.'

    def handle(self, *args, **options):
        outdir = self.output_dir(*args, **options)
        num_files, num_bytes = 0, 0
        for ufile in File.objects.all():
            num_bytes += self.write(ufile, outdir)
            num_files += 1
        self.stdout.write('Exported {} bytes to {} files.'.format(num_bytes, num_files))

    def output_dir(self, *args, **options):
        print(args, options)
        if len(args) != 1:
            raise CommandError('First and only argument must be output directory.')
        outdir = args[0]
        if not os.path.isdir(outdir):
            raise CommandError('Not a directory: ' + outdir)
        if not os.access(outdir, os.R_OK | os.W_OK | os.X_OK):
            raise CommandError('No RWX access on directory, will not be able to write files: ' + outdir)
        if os.listdir(outdir):
            raise CommandError('Directory not empty, refusing to overwrite files: ' + outdir)
        return outdir

    def write(self, ufile, outdir):
        if not re.match(r'^[a-zA-Z0-9._-]+$', ufile.name) or '..' in ufile.name:
            raise CommandError('Invalid filename, refusing to write: ' + ufile.name)

        if ufile.size != len(ufile.body):
            raise CommandError('Size mismatch of {} body: size {} bytes, actual body {} bytes.'.format(ufile.name, ufile.size, len(ufile.body)))

        filename = os.path.join(outdir, ufile.name)
        with open(filename, 'wb') as f:
            f.write(ufile.body)

        if ufile.size != os.path.getsize(filename):
            raise CommandError('Size mismatch after write of {}: expected {} bytes, wrote {} bytes.'.format(ufile.name, ufile.size, os.path.getsize(filename)))

        self.stdout.write('Wrote {} bytes to {}'.format(ufile.size, filename))
        return ufile.size
