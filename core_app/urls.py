from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import Login,RegisterUser

urlpatterns = [
    path('home/', views.home, name='home'),
    path('product_list/', views.productList, name='pdlist'),
    path('product_list/<int:p_id>', views.productList, name='pdlist'),
    path('productForm/', views.productForm, name='pdform' ),
    path('updateForm/<int:p_id>', views.updateProductForm, name='pdupdateform' ),
    path('productDetail/<int:p_id>', views.productDetail, name='pddetail' ),
    path('productdelete/<int:p_id>',views.productDelete,name='pddelete'),
    # path('productdeleted/<int:p_id>',views.productActualDelete,name='actualdelete'),

    path('orderlist/',views.orderList,name='odlist'),
    path('orderlist/orderform/',views.orderForm,name='odform'),
    path('orderlist/orderupdateform/<int:o_id>',views.orderUpdateForm,name='odupdateform'),
    path('orderlist/orderdetail/<int:o_id>',views.orderDetail,name='oddetail'),
    path('orderlist/orderprod/',views.order_products,name='orderProd'), 

    path('supplylist',views.supplierlist,name='splist'),
    path('supplylist/<int:sp_id>',views.supplierlist,name='splist'),
    path('supplylist/supplierform/',views.supplierForm,name='spform'),
    path('supplylist/supplierproductlist/<int:supplier_id>',views.supplierProducts,name='spproduct'),
    path('supplierUpdateForm/<int:sp_id>',views.supplierupdateform,name='spupdateform'),
    path('supplierdelete/<int:sp_id>',views.supplierdelete,name='spdelete'),

    path('customerlist/',views.customerList,name='cmlist'),
    path('customerlist/<int:c_id>', views.customerList, name='cmlist'),
    path('customerdetail/<int:c_id>',views.customerdetail,name='cmdetail'),
    path('customerUpdateForm/<int:c_id>',views.customerupdateform,name='cmupdateform'),
    path('customerlist/customerform/',views.customerForm,name='cmform'),
    path('customerdelete/<int:c_id>',views.customerDelete,name='cmdelete'),

    path('',views.login_,name='login'),
    path('logout/',views.logout_,name='logout'),
    path('sign/',views.signup_data,name='sign')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)