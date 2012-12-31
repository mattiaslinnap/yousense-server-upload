yousense-upload
===============

Re-usable Django app for YouSense uploads backend.

The API accepts bulk sensor data uploads from YouSense mobile clients.
It does not validate or parse the uploads, this is left to background tasks via celery.