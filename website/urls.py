from django.urls import path, include
from .views import *

# from .views_.request import *
# from .views_.request_child import *
# from .views_.site import *
# from .views_.profile import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),

    path('user_profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('user_profile/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),

    path('about/', AboutPageView.as_view(), name='about'),

    path('catalog/list/', CatalogListView.as_view(), name='catalog-list'),
    path('catalog/detail/<int:pk>/', CatalogDetailView.as_view(), name='catalog-detail'),

    path('procedure/list/', ProcedureListView.as_view(), name='procedure-list'),
    path('procedure/detail/<int:pk>/', ProcedureDetailView.as_view(), name='procedure-detail'),

    path('basket/list/', BasketListView.as_view(), name='basket-list'),
    path('basket/product-add/<int:pk_product>/', basket_product_add, name='basket-product-add'),
    path('basket/product-update/<int:pk>/', BasketUpdateView.as_view(), name='basket-product-update'),
    path('basket/product-delete/<int:pk>/', BasketDeleteView.as_view(), name='basket-product-delete'),
    path('basket/composed/', basket_composed, name='basket-composed'),

    path('report/detail/', ReportSettingsDetailView.as_view(), name='report-settings-detail'),
    path('report/update/', ReportSettingsUpdateView.as_view(), name='report-settings-update'),
    path('report/sale-list/', ReportSaleListView.as_view(), name='report-sale-list'),
    path('report/report-sale-list-by-user/', ReportSaleListByUserView.as_view(), name='report-sale-list-by-user'),
    path('report/report-service-stat-by-user/', ReportServiceStatByUserView.as_view(), name='report-service-stat-by-user'),

    path('request/list/', RequestListView.as_view(), name='request-list'),
    path('request/detail/<int:pk>/', RequestDetailView.as_view(), name='request-detail'),
    path('request/create/', RequestCreateView.as_view(), name='request-create'),
    path('request/create/<int:procedure_id>/', RequestCreateView.as_view(), name='request-create-by-id'),
    path('request/update/<int:pk>/', RequestUpdateView.as_view(), name='request-update'),
    path('request/delete/<int:pk>/', RequestDeleteView.as_view(), name='request-delete'),
]
