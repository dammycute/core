
from django.contrib import admin
from django.urls import path, include, re_path
# from business.views import *
from rest_framework.routers import DefaultRouter

from proper.views import DashboardView
# urlpatterns = router.urls,
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

...

swagger_settings = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },

    'SECURITY_REQUIREMENTS': {
        'Bearer': []
    }
}

schema_view = get_schema_view(
   openapi.Info(
      title="RealOwn API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://realowndigital.com/terms.html",
      contact=openapi.Contact(email="realowndigital@gmail.com"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)



urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("", DashboardView.as_view(), name='Dashboard'),
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('api-auth/', include('rest_framework.urls')),
    path('user/', include('business.urls')),
    path('product/', include('proper.urls')),
    # path('auth/', include('drf_social_oauth2.urls', namespace='drf'))
    # path('', include(router.urls)),
    # path('unique', UniquePropertyView.as_view()),
    # path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    

]
