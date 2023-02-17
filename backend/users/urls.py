# from django.contrib.auth.views import LogoutView, LoginView
# from django.urls import include, path
# from rest_framework.routers import DefaultRouter

# app_name = 'users'

# router = DefaultRouter()

# urlpatterns = [
#     path('', include(router.urls)),
#     path(
#         'login/',
#         LoginView.as_view(template_name='users/login.html'),
#         name='login'
#     ),
#     path(
#       'logout/',
#       LogoutView.as_view(template_name='users/logged_out.html'),
#       name='logout'
#     ),
# ]