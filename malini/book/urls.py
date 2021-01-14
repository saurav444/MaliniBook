from django.urls import path

from . import views
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name='detail'),
    path('science/', ScienceView.as_view(), name='science'),
    path('commerce/', CommerceView.as_view(), name='commerce'),
    path('govt/', GovtView.as_view(), name='govt'),
    path('religious/', ReligiousView.as_view(), name='religious'),
    path('story/', StoryView.as_view(), name='story'),
    path('arts/', ArtsView.as_view(), name='arts'),
    path('cart<int:pro_id>/', AddToCartView.as_view(), name='cart'),
    path('my_cart/', MyCartView.as_view(), name='my_cart'),
    path('manager_cart/<int:cp_id>/', ManagerCartView.as_view(), name='manager_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('register/', CustomerRegistrationView.as_view(), name='register'),
    path('logout/', CustomerLogoutView.as_view(), name='logout'),
    path('login/', CustomerLoginView.as_view(), name='login'),
    path('forgot-password/', PasswordForgotView.as_view(), name='passwordforgot'),
    path('profile/', CustomerProfileView.as_view(), name='profile'),
    path('profile/order-<int:pk>/', CustomerOrderDetailView.as_view(), name='customerorderdetail'),
    path('admin-login/', AdminLoginView.as_view(), name='adminlogin'),
    path('admin-home/', AdminHomeView.as_view(), name='adminhome'),
    path('admin-order/<int:pk>/', AdminOrderDetailView.as_view(), name='adminorderdetail'),
    path('admin-all-orders/', AdminOrderListView.as_view(), name='adminorderlist'),
    path('admin-order<int:pk>-change/', AdminOrderStatusView.as_view(), name='adminordestatuschange'),
    path('search/', SearchView.as_view(), name='search'),
    ]