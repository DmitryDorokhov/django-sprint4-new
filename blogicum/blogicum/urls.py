from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'pages.views.page_not_found'
handler403 = 'pages.views.custom_403'
handler500 = 'pages.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += (path('__debug__/', include('debug_toolbar.urls')),)
