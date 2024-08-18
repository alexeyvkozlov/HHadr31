from .models import Employer
from .serializers import EmployerSerializer
from rest_framework import viewsets


class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer