import datetime

from django.db import models
from simple_history.models import HistoricalRecords


class Label(models.Model):
    slug = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.slug}"


class DocumentLabel(models.Model):
    document = models.ForeignKey("sh.Document", on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.PROTECT)


class Document(models.Model):
    name = models.CharField(max_length=50)
    labels = models.ManyToManyField(Label, through=DocumentLabel)
    history = HistoricalRecords(m2m_fields=[labels])
    __history_date = None

    @property
    def _history_date(self):
        # return self.__history_date
        return (
            self.__history_date
            if self.__history_date is not None
            else datetime.datetime.now().astimezone(datetime.timezone.utc)
        )

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    def __str__(self):
        return f"{self.name}"

    def update_history_date(self, year, month, day, hour=0, minutes=0, seconds=0):
        h = self.history.latest()  # .most_recent()?
        h.history_date = datetime.datetime(
            year, month, day, hour, minutes, seconds
        ).astimezone(datetime.timezone.utc)
        h.save()


def explore():
    """

    >>> Document.objects.count()
    0

    >>> d=Document.objects.create(name="doc one")
    >>> d.update_history_date(2024,1,1)

    >>> d.labels.count()
    0

    >>> _ = d.labels.create(slug="red")
    >>> d.update_history_date(2024,2,1)
    >>> _ = d.labels.create(slug="green")
    >>> d.update_history_date(2024,3,1)
    >>> _ = d.labels.create(slug="blue")
    >>> d.update_history_date(2024,4,1)

    >>> d.labels.count()
    3

    >>> for h in d.history.all():
    ...     print(h, ", ".join([dl.label.slug for dl in h.labels.all()]))
    doc one as of 2024-04-01 00:00:00+00:00 red, green, blue
    doc one as of 2024-03-01 00:00:00+00:00 red, green
    doc one as of 2024-02-01 00:00:00+00:00 red
    doc one as of 2024-01-01 00:00:00+00:00 

    >>> from itertools import pairwise
    >>> for (a,b) in pairwise(d.history.all()):
    ...     print(f"Comparing {a} to {b}")
    ...     for change in a.diff_against(b).changes:
    ...         print(f"'{change.field}' changed from '{change.old}' to '{change.new}'")
    Comparing doc one as of 2024-04-01 00:00:00+00:00 to doc one as of 2024-03-01 00:00:00+00:00
    'labels' changed from '[{'document': 1, 'label': 1}, {'document': 1, 'label': 2}]' to '[{'document': 1, 'label': 1}, {'document': 1, 'label': 2}, {'document': 1, 'label': 3}]'
    Comparing doc one as of 2024-03-01 00:00:00+00:00 to doc one as of 2024-02-01 00:00:00+00:00
    'labels' changed from '[{'document': 1, 'label': 1}]' to '[{'document': 1, 'label': 1}, {'document': 1, 'label': 2}]'
    Comparing doc one as of 2024-02-01 00:00:00+00:00 to doc one as of 2024-01-01 00:00:00+00:00
    'labels' changed from '[]' to '[{'document': 1, 'label': 1}]'

    >>> for (a,b) in pairwise(d.history.all()):
    ...     print(f"Comparing {a} to {b}")
    ...     for change in a.diff_against(b).changes:
    ...         labels_old = list(Label.objects.filter(pk__in=[t["label"] for t in change.old]).values_list("slug",flat=True))
    ...         labels_new = list(Label.objects.filter(pk__in=[t["label"] for t in change.new]).values_list("slug",flat=True))
    ...         print(f"'{change.field}' changed from '{labels_old}' to '{labels_new}'")
    Comparing doc one as of 2024-04-01 00:00:00+00:00 to doc one as of 2024-03-01 00:00:00+00:00
    'labels' changed from '['red', 'green']' to '['red', 'green', 'blue']'
    Comparing doc one as of 2024-03-01 00:00:00+00:00 to doc one as of 2024-02-01 00:00:00+00:00
    'labels' changed from '['red']' to '['red', 'green']'
    Comparing doc one as of 2024-02-01 00:00:00+00:00 to doc one as of 2024-01-01 00:00:00+00:00
    'labels' changed from '[]' to '['red']'
    """

    pass
