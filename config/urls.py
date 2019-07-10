from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

core_schema_view = include_docs_urls(title='Authors Haven Space  API')
schema_view = get_swagger_view(title='Authors Haven Space  API')

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('api/', include(('authors.apps.authentication.urls', 'authentication'), namespace='auth')),
    path('swagger/', schema_view),
    path('', core_schema_view),
    path('api/', include(('authors.apps.articles.urls', 'articles'), namespace='article')),
    path('api/articles/', include(('authors.apps.comments.urls', 'comments'), namespace='comments')),
    path('api/profiles/', include(('authors.apps.profiles.urls', 'profiles'),  namespace='profiles')),
    path('api/', include('authors.apps.social_auth.urls', namespace='social-auth')),
]

if settings.DEBUG:
    urlpatterns += [
        path('400/', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        path('403/', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        path('404/', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        path('500/', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
