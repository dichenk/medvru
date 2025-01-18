from django.urls import path
from .views import RpcView


urlpatterns = [
    path('', RpcView.as_view(), name='rpc'),
]
