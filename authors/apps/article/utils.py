from rest_framework import serializers

from django.utils.text import slugify

from .models import Tag


class TagField(serializers.ModelSerializer):
    """
    to cater for Tag field
    """
    def get_queryset(self):
        res = Tag.objects.all()
        return res
    
    def to_internal_value(self,data):
        tag, created = Tag.objects.get_or_create(
            tag=data, slug=slugify(data.lower())
        )
        