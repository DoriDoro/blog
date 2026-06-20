from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.defaults import page_not_found, server_error

urlpatterns = [
    # --------------------
    # Django Admin
    # --------------------
    path("admin/", admin.site.urls),
    # ------------------------
    # Django Application URLs
    # ------------------------
    path("accounts/", include("accounts.urls", namespace="accounts")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__preview__/404/", page_not_found, {"exception": Exception("Preview 404")}),
        path("__preview__/500/", server_error),
    ]
if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
