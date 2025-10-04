from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('adedamola/', admin.site.urls),
    path('v1/authentication/', include('authentication.urls')),
    path('v1/base/', include('base.urls')),
    path('v1/cart/', include('cart.urls')),
    path('v1/users/', include('users.urls')),
    path('v1/products/', include('products.urls')),
    path('v1/payment/', include('payment.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)