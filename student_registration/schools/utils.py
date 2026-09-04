import io
import xlwt
from datetime import date , datetime
from import_export import resources, fields
from django.http import HttpResponse, FileResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Color
from .models import (
    School,
    Club,
    Meeting,
    CommunityInitiative,
    HealthVisit
)
import copy
from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)


def is_allowed_create(programme):
    """Check whether creation actions are allowed for the given programme.

    Args:
        programme (str): Programme name such as ``"Bridging"``.

    Returns:
        bool: ``True`` when within the configured creation window, otherwise ``False``.
    """
    from .models import CLMRound
    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'Bridging':
            # first(), not get(): with no round flagged current - which is the
            # normal state between rounds - get() raised DoesNotExist and every
            # page that asks this question logged a full traceback.
            current_round = current_round.filter(current_round_bridging=True).first()
            if not current_round:
                return False
            if not (current_round.start_date_bridging and current_round.end_date_bridging):
                return False
            return current_round.start_date_bridging < current < current_round.end_date_bridging

        return False

    except Exception as ex:
        logger.exception(ex)
        return False


def is_allowed_edit(programme):
    """Check whether edit actions are allowed for the given programme.

    Args:
        programme (str): Programme name such as ``"Bridging"``.

    Returns:
        bool: ``True`` when current date falls in the edit window, otherwise ``False``.
    """
    from .models import CLMRound

    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'Bridging':
            # See is_allowed_create: no current round is an ordinary state, not
            # an error worth a traceback per request.
            current_round = current_round.filter(current_round_bridging=True).first()
            if not current_round:
                return False
            if not (current_round.start_date_bridging_edit and current_round.end_date_bridging_edit):
                return False
            return current_round.start_date_bridging_edit < current < current_round.end_date_bridging_edit

        return False

    except Exception as ex:
        logger.exception(ex)
        return False


def listToString(s):
    """Join a list of strings with comma separators.

    Args:
        s (list[str]): Strings to concatenate.

    Returns:
        str: Comma-delimited string of all elements.
    """
    str1 = ""

    for ele in s:
        if str1 == "":
            str1 += ele
        else:
            str1 += "," + ele

    return str1


class MemorySavingQuerysetIterator(object):
    """Iterate through a queryset in smaller batches to reduce memory usage."""

    def __init__(self, queryset, max_obj_num=1000):
        """Initialize the iterator with the queryset and chunk size.

        Args:
            queryset (QuerySet): Django queryset to iterate through.
            max_obj_num (int, optional): Number of objects to fetch per batch.
        """
        self._base_queryset = queryset
        self._generator = self._setup()
        self.max_obj_num = max_obj_num

    def _setup(self):
        """Yield objects from the queryset in configured chunk sizes.

        Yields:
            Model: Instances from the underlying queryset.
        """
        for i in xrange(0, self._base_queryset.count(), self.max_obj_num):
            # By making a copy of the queryset and using that to actually access
            # the objects we ensure that there are only `max_obj_num` objects in
            # memory at any given time
            smaller_queryset = copy.deepcopy(self._base_queryset)[i:i + self.max_obj_num]
            # logger.debug('Grabbing next %s objects from DB' % self.max_obj_num)
            for obj in smaller_queryset.iterator():
                yield obj

    def __iter__(self):
        """Return the iterator instance."""
        return self

    def next(self):
        """Return the next object from the generator.

        Returns:
            Model: Next instance in the queryset iteration.
        """
        return self._generator.next()
