from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', blog_views.register, name='register'),
    path('', include('blog.urls', namespace='blog')),
]

handler403 = 'blog.views.csrf_failure'
handler404 = 'blog.views.handler404'
handler500 = 'blog.views.handler500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
