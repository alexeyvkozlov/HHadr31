# from django.conf.urls import url, include
from .models import Employer
from rest_framework import routers, serializers, viewsets


class EmployerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'
