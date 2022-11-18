from django.contrib import admin
from django.urls import include, path
from polls import urls as polls_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(polls_urls)),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]