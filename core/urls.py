from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('logout/', views.logout_redirect, name='logout'),
    
    # URLs para probar manejo de errores (solo en desarrollo)
    path('test/404/', views.test_404_view, name='test-404'),
    path('test/500/', views.test_500_view, name='test-500'),
    path('test/403/', views.test_403_view, name='test-403'),
    path('test/400/', views.test_400_view, name='test-400'),
]

