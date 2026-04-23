from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("predict/", views.predictAll),  # POST request with JSON body
    path("predict/logd/", views.predictLogD),  # POST request with JSON body
    path("predict/logs/", views.predictLogS),  # POST request with JSON body
    path("predict/<str:structure>/", views.predictAll),  # Legacy GET support
    path("predict/logd/<str:structure>/", views.predictLogD),
    # Legacy GET support
    path(
        "predict/logs/<str:structure>/",
        views.predictLogS),
    # Legacy GET support
]
