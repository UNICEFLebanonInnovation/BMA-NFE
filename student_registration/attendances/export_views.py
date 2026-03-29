from __future__ import absolute_import, unicode_literals

import csv
import io
import codecs
import datetime
import logging
import os
import traceback
import uuid

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import connection
from django.http import HttpResponse
from django.urls import reverse
from storages.backends.azure_storage import AzureStorage

from student_registration.backends.models import ExportHistory
from student_registration.users.templatetags.custom_tags import has_group