from django.contrib import admin
from django.urls import path

from account import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('registration/', account_views.registration),
    path('auth/', account_views.auth),

    path('', account_views.PersonalAccountView.as_view(), name='personal_account_view'),
    path('roles/', account_views.RolesView.as_view(), name='roles_view'),
    path('profiles/', account_views.ProfilesView.as_view(), name='profiles_view'),
    path('profiles/user_<str:profile_id>', account_views.single_profile, name='single_profiles_view'),

]
