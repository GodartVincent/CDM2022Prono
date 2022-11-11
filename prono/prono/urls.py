from django.contrib import admin
from django.urls import include, path
from polls import urls as polls_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('polls/', include(polls_urls)),
]