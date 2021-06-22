from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'eventpath_mapper.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/', "entries2.views.upload_gs_json", name="upload_gs_json"),
    url(r'^upload_action/', "entries2.views.upload_action", name="upload_action")
]
