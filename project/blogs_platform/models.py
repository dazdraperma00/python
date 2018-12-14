from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hitcount.models import HitCountMixin, HitCount

status_choices = (
    ('v', 'Visible'),
    ('h', 'Hidden')
)


class Post(models.Model, HitCountMixin):
    subject = models.CharField(u'Тема', max_length=255)
    text = models.TextField(u'Текст')
    status = models.CharField(max_length=1, default='v', choices=status_choices)
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    def is_visible(self):
        if self.status == 'v':
            return True
        return False

    def __str__(self):
        return '{} | {}'.format(self.pk, self.subject)


class Comment(models.Model):
    text = models.TextField(u'Текст')
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    author_nick = models.CharField(u"Автор", max_length=255)
    creation_date = models.DateTimeField("Дата создания", auto_now_add=True)
    reply_to = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return '{} | {}'.format(self.pk, self.author_nick)
