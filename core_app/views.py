from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login,logout, get_user_model,authenticate
from .models import Product
from .models import Supplier
from .models import Customer
from .models import Order,OrderItem
from django.contrib import messages
from django.utils import timezone
from django.db.models import F

User = get_user_model()
# from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# from django.contrib.auth.views import LoginView
# from django.views.generic.edit import FormView
# from .forms import RegisterUserForm
# from django.contrib.auth import login


# Create your views here.
def home(req):
    lowstock = (Product.objects.filter(user=req.user,current_stock__lt = F('reorder_level'))).count()
    productCount = Product.objects.filter(user=req.user).count()
    supplierCount = Supplier.objects.filter(user=req.user).count()
    customerCount = Customer.objects.filter(user=req.user).count()
    orderCount = Order.objects.filter(user=req.user).count()
    prodlist = Product.objects.filter(user=req.user)
    ordlist = Order.objects.select_related('customer').prefetch_related('items__product').filter(user=req.user)
    context = {'pdcount':productCount,
               'spcount':supplierCount,
                'cstcount':customerCount,
                'ordercount':orderCount,
                'lowstock':lowstock,
                'prodlist':prodlist,
                'ordlist':ordlist

    }
    return render(req, "core_app/home.html",{'context':context})   
 
def productList(request,p_id=0):
    if(p_id!=0):
        product = Product.objects.get(product_id = p_id )
        product.delete()
        print("Product deleted")
    prodlist = Product.objects.filter(user=request.user)
    
    return render(request, "core_app/products/product_list.html",{'prodlist':prodlist}) 

def updateProductForm(req,p_id):
    error=None
    product = Product.objects.get(product_id = p_id)
    print("update form")
    supplierNames = Supplier.objects.values_list('name', flat=True)
    if req.method == 'POST':
        try:
          product.name = req.POST.get('product_name')
          product.product_Img = req.FILES.get('product_img')
          product.category = req.POST.get('category')
          product.current_stock = req.POST.get('stock')
          product.price = req.POST.get('price')
          product.reorder_level = req.POST.get('reorder_level')
          product.description = req.POST.get('description')
          product.supplier = req.POST.get('supplier')
          product.save()
          return redirect('pdlist') 
        except Exception as e:
            error=str(e)
    return render(req,"core_app/products/product_UpdateForm.html",{"err":error,'products':product,"supplierList":supplierNames})

def productForm(req):
    error=None
    supplierNames = Supplier.objects.values_list('name', flat=True)
    if req.method == 'POST':
        product_Name = req.POST.get('product_name')
        product_img = req.FILES.get('product_img')
        sku = req.POST.get('sku')
        category = req.POST.get('category')
        curr_stock = req.POST.get('stock')
        price = req.POST.get('price')
        reorder_lvl = req.POST.get('reorder_level')
        descrp = req.POST.get('description')
        supplier_=req.POST.get('supplier')
        try:
            Product.objects.create(user=req.user,name=product_Name,sku=sku,category=category,current_stock=curr_stock,price=price,reorder_level=reorder_lvl,description=descrp,supplier=supplier_ ,product_Img=product_img)
            succ = "Product saved successfully!"
            messages.success(req, succ)
            return redirect("pdlist")
        except Exception as e:
            error =str(e)   
    return render(req, "core_app/products/product_form.html",{"err":error,"supplierList":supplierNames})
     
def productDetail(request,p_id):
    context = Product.objects.get(product_id = p_id)
    return render(request, "core_app/products/product_details.html",{'context':context}) 


def productDelete(request,p_id):
    context = Product.objects.get(product_id = p_id)
    return render(request, "core_app/products/product_delete.html",{'context':context}) 

def orderList(req):
    ordlist = Order.objects.select_related('customer').prefetch_related('items__product').filter(user=req.user)
    return render(req, "core_app/orders/orderlist.html",{'ordlist':ordlist})

def orderUpdateForm(req,o_id):
    error=None
    order = Order.objects.get(order_id = o_id)
    orderitem = OrderItem.objects.select_related('product').filter(order_id = o_id)
    print(orderitem)
    prodlist = Product.objects.filter(user=req.user)
    customers = Customer.objects.all()
    if req.method == 'POST':
        
        product_ids = req.POST.getlist('product_id[]') 
        quantities = req.POST.getlist('quantity[]')
        item_prices = req.POST.getlist('item_price[]')
        try:
          order.order_date = timezone.now()
          order.tax = req.POST.get('tax-amount')
          order.sub_total = req.POST.get('subtotal-amount')
          order.total_cost = req.POST.get('total-amount')
          order.customer_id = int(req.POST.get('customer'))
          order.save()
          order_items_to_create = []
          product_qnty = {}
          for item in orderitem:
           for pd,qn,pr in zip(product_ids,quantities,item_prices):
             product_id = int(pd)
             quantity = int(qn) 
             item.quantity=int(qn)
             item.price=pr
             item.product_id=product_id
             item.save()
             product_qnty[product_id] = product_qnty.get(product_id, 0) + quantity
          for p_id , p_qty in product_qnty.items():
                print(type(p_qty))
                Product.objects.filter(product_id=p_id).update(current_stock = F('current_stock') - p_qty)
          return redirect('odlist') 
        except Exception as e:
            error=str(e)
    return render(req,"core_app/orders/order_updateform.html",{"err":error,'order':order,'customers':customers,'prodlist':prodlist,'orderitem':orderitem})

def orderForm(req):
    error=None
    customers = Customer.objects.filter(user=req.user)
    prodlist = Product.objects.filter(user=req.user)
    if req.method == 'POST':
        cst_id = int(req.POST.get('customer'))
        subtotal = req.POST.get('subtotal-amount')
        taxamt = req.POST.get('tax-amount')
        total = req.POST.get('total-amount')
        
        product_ids = req.POST.getlist('product_id[]') 
        quantities = req.POST.getlist('quantity[]')
        item_prices = req.POST.getlist('item_price[]')
               
        try:            
            new_order = Order.objects.create(user=req.user,customer_id=cst_id,order_date=timezone.now(),tax=taxamt,sub_total=subtotal,total_cost=total)
            order_items_to_create = []
            product_qnty = {}
            for pd,qn,pr in zip(product_ids,quantities,item_prices):
              product_id = int(pd)
              quantity = int(qn)
              OrderItem.objects.create(user=req.user,quantity=int(qn),price=pr,order_id=new_order.order_id,product_id=product_id)            
              product_qnty[product_id] = product_qnty.get(product_id, 0) + quantity
            OrderItem.objects.bulk_create(order_items_to_create)
            for p_id , p_qty in product_qnty.items():
                print(type(p_qty))
                Product.objects.filter(product_id=p_id).update(current_stock = F('current_stock') - p_qty)
            succ = "Order saved successfully!"
            messages.success(req, succ)
            return render(req, "core_app/products/order_form.html",{"success":succ,'prodlist':prodlist,'customers':customers})
        except Exception as e:
            print(e)
            error =str(e)    
    return render(req, "core_app/orders/order_form.html",{"err":error,'prodlist':prodlist,'customers':customers})

def orderDetail(request,o_id):
    orders = Order.objects.select_related('customer').prefetch_related('items__product').get(pk=o_id)
    orderitems = OrderItem.objects.filter(order_id = o_id)
    combined = zip(orders.items.all(),orderitems)
    return render(request, "core_app/orders/order_detail.html",{'orders':orders,'combined':combined})

def order_products(request):
    return render(request, "core_app/orders/order_products.html")

def supplierlist(req,sp_id=0):
    if(sp_id!=0):
        supplier = Supplier.objects.get(supplier_id = sp_id )
        supplier.delete()
        print("Customer deleted")
    splList = Supplier.objects.filter(user=req.user)
    return render(req, "core_app/suppliers/suppliers_list.html",{'splList':splList})

def supplierForm(req):
    error=None
    if req.method == 'POST':
        Name = req.POST.get('supplier_name')
        contact = req.POST.get('contact_person')
        mail = req.POST.get('email')
        phone = req.POST.get('phone')
        street_addrs = req.POST.get('address_line1')
        city = req.POST.get('city')
        state = req.POST.get('state')
        zip = req.POST.get('zip')
        country = req.POST.get('country')
        try:
            Supplier.objects.create(user=req.user,name=Name,contact_person=contact,email=mail,phone=phone,street_address=street_addrs,city=city,state_province=state,zip_postal_code=zip,country=country)
            succ = "Supplier registered successfully!"
            messages.success(req, succ)
            return redirect("splist")
        except Exception as e:
            error =str(e)
    return render(req, "core_app/suppliers/suppliers_form.html",{"err":error})

def supplierProducts(request,supplier_id):
    supplier=Supplier.objects.get(supplier_id=supplier_id)
    supplierName=supplier.name
    prodList = Product.objects.filter(supplier=supplierName)
    return render(request, "core_app/suppliers/suppliers_productList.html",{'ProdList':prodList,"supplierName":supplierName})

def supplierupdateform(req,sp_id):
    error=None
    supplier = Supplier.objects.get(supplier_id = sp_id)
    if req.method == 'POST':
        try:
          supplier.name = req.POST.get('supplier_name')
          supplier.contact_person = req.POST.get('contact_person')
          supplier.email = req.POST.get('email')
          supplier.phone = req.POST.get('phone')
          supplier.street_address = req.POST.get('address_')
          supplier.city = req.POST.get('city')
          supplier.state_province = req.POST.get('state')
          supplier.zip_postal_code = req.POST.get('zip')
          supplier.country = req.POST.get('country')
          supplier.save()
          return redirect('splist') 
        except Exception as e:
            error=str(e)
    return render(req,"core_app/suppliers/supplier_update.html",{"err":error,'supplier':supplier})

def supplierdelete(req,sp_id):
    context = Supplier.objects.get(supplier_id = sp_id)
    return render(req,"core_app/suppliers/supplier_delete.html",{'context':context})

def customerList(request,c_id=0):
    if(c_id!=0):
        customer = Customer.objects.get(Customer_id = c_id )
        customer.delete()
        print("Customer deleted")
    cstlist = Customer.objects.filter(user=request.user)
    return render(request, "core_app/customer/customer_list.html",{'cstList':cstlist})

def customerdetail(request,c_id):
    print(c_id)
    context = Customer.objects.get(Customer_id = c_id)
    return render(request, "core_app/customer/customer_detail.html",{'context':context}) 

def customerupdateform(req,c_id):
    error=None
    customer = Customer.objects.get(Customer_id = c_id)
    if req.method == 'POST':
        try:
          customer.name = req.POST.get('customer_name')
          customer.customer_Img = req.FILES.get('customer_img')
          customer.email = req.POST.get('email')
          customer.phone = req.POST.get('phone')
          customer.address = req.POST.get('address_')
          customer.city = req.POST.get('city')
          customer.state_province = req.POST.get('state')
          customer.zip_postal_code = req.POST.get('zip')
          customer.country = req.POST.get('country')
          customer.save()
          return redirect('cmlist') 
        except Exception as e:
            error=str(e)
    return render(req,"core_app/customer/customer_updateform.html",{"err":error,'customer':customer})

def customerForm(req):
    error=None
    if req.method == 'POST':
        Name = req.POST.get('customer_name')
        customer_img = req.FILES.get('customer_img')
        mail = req.POST.get('email')
        phone = req.POST.get('phone')
        address = req.POST.get('address_')
        city = req.POST.get('city')
        state = req.POST.get('state')
        zip = req.POST.get('zip')
        country = req.POST.get('country')
        try:
            Customer.objects.create(user=req.user,name=Name,email=mail,phone=phone,address=address,city=city,state_province=state,zip_postal_code=zip,country=country,customer_Img=customer_img)
            succ = "Supplier registered successfully!"
            messages.success(req, succ)
            return redirect("cmlist")
        except Exception as e:
            error =str(e)
    return render(req, "core_app/customer/customer_form.html",{"err":error})

def customerDelete(request,c_id):
    context = Customer.objects.get(Customer_id = c_id)
    return render(request, "core_app/customer/customer_delete.html",{'context':context}) 

# def login_(req):
#     return render(req,'core_app/authentication/login.html')  

def signup_data(req):
    if req.method == 'POST':
        form = CustomUserCreationForm(req.POST)
        if form.is_valid():
            user = form.save()
            login(req,user)
            return redirect('login')
    else:
        initial_data = {'username':"",'email':'','password1':"",'password2':""}
        form= CustomUserCreationForm(initial=initial_data)
    return render(req,"core_app/authentication/signup.html",{'form':form})  


def login_(req):
    error = ""
    if req.method == "POST":
        identifier = req.POST.get("username",'').strip()
        password = req.POST.get("password",'').strip()
        print(identifier)
        print(password)
        try:
            if "@" in identifier:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            else:
                username = identifier
        except User.DoesNotExist:
            username = None
        
        if username:
            user = authenticate(req, username=username, password=password)
            print(f"Authenticated user: {user}")
            if user is not None:
                login(req, user)
                return redirect('home')
            else:
                error = "Invalid username/email or password"
        else:
            print('username',username)
            error = "User not founding"
        return render(req, "core_app/authentication/login.html", {'err': error})
    else:
        print("request is not post")
        initial_data = {'username':"",'password':""}
        form = AuthenticationForm(initial=initial_data)
    return render(req, "core_app/authentication/login.html", {'form': form})

def logout_(req):
    logout(req)
    return redirect('login')

# def product_form_data(req):
#     error=None
#     if req.method == 'POST':
#         product_Name = req.POST.get('product_name')
#         sku = req.POST.get('sku')
#         category = req.POST.get('category')
#         curr_stock = req.POST.get('stock')
#         price = req.POST.get('price')
#         reorder_lvl = req.POST.get('reorder_level')
#         descrp = req.POST.get('description')
#         print(product_Name)
#         print(sku)
#         print(category)
#         print(curr_stock)
#         print(price)
#         print(reorder_lvl)
#         print(descrp)
#         try:
#             prod = Product(name=product_Name,sku=sku,category=category,current_stock=curr_stock,price=price,reorder_level=reorder_lvl,description=descrp)
#             prod.save()
#             succ = "Product saved successfully!"
#             return render(req, "core_app/products/product_form.html",{"success":succ})
#         except Exception as e:
#             error =str(e)
    
#     return render(req, "core_app/products/product_form.html",{"err":error})