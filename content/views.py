from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings
from .models import Trader_Product_Data, Customer, Customer_Bill
from datetime import datetime,date
# from django.db.models import Q
from django.utils import timezone
import decimal
from django.db.models import Sum,Q



# Create your views here.

def home(request):
    failed = 0

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None :
            current_manager = Current_manager.objects.filter(user = user).first()
            if current_manager != None  and current_manager.active_status == 1:
                request.session.set_expiry(0)
                failed =0
                login(request, user)
                print('username: ' + request.user.username + ' has log in to system at ' + str(datetime.now()))
                # return redirect("content:receipt_net")
                return redirect("content:store")
            else :
                failed =1
        else:
            failed =1
    context = {'failed' : failed}
    return render(request, 'content/login.html', context = context)
    return render(request, 'content/login.html')

@login_required
def logout_view(request):

    if request.user != None:
            userna = request.user.username
            logout(request)
            print('username: ' + userna + ' has log out of system at ' + str(datetime.now()))

    return redirect('content:login-page')


@login_required
def manager(request,manager_id):

        context = {

        }
        return render(request, 'content/manager.html',context = context)


@login_required
def store(request):

        products = Product.objects.all().order_by("name")

        total = 0
        if products != None :
            total = sum(p.total_cost for p in products)
        # products = sorted(products, key=lambda x:x.total_quantity, reverse = True)
        context = {
            'products':products,
            'total':round(total,1),
        }
        # print( len(products))

        return render(request, 'content/store.html',context = context)




@login_required
def Treasury_receipt(request):
    current_manager = Current_manager.objects.filter(user = request.user).first()
    transactions = Safe_data.objects.filter(day__date__gte = current_manager.start_date , day__date__lte=  current_manager.end_date).order_by('-id')
    m_safe = Safe_Month.objects.last()
    context = {
        'transactions':transactions,
        'safe':m_safe,
    }
    return render(request, 'content/Treasury_receipt.html',context)



@login_required
def monthly_receipt(request):


    return render(request, 'content/monthly_receipt.html')


@login_required
def withdrawings_all(request):
    current_manager = Current_manager.objects.filter(user = request.user).first()
    transactions = withdrawings.objects.filter(day__date__gte = current_manager.start_date , day__date__lte=  current_manager.end_date).order_by('-id')
    total_tr_money = 0

    for t in transactions:
        total_tr_money += t.money_amount
    context = {
        'transactions':transactions,
        'total_tr_money':total_tr_money,
    }
    return render(request, 'content/withdrawings.html',context)




@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def treasury_transactions(request):
    success = failed =0

    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now()
        amount = float(request.POST['amount'])
        manager = Current_manager.objects.get(user = request.user)
        notes = request.POST['notes']
        ## get current manager safe
        m_safe = Safe_Month.objects.last()

        ## test amount against trader remaining_money
        if amount < 0:
            if  m_safe.money >= abs(amount)  :
                m_safe.money -= abs(amount)
                m_safe.save()

                Safe_data.objects.create(day = date, money_amount = amount, given_person =manager, notes=notes ,safe_line_status = 6 )
                success = 1
            else:
                failed = 1

        elif amount > 0 : ## positive amount
            m_safe.money += amount
            m_safe.save()

            Safe_data.objects.create(day = date, money_amount = amount, given_person =manager, notes=notes )
            success = 1



    today_date =  timezone.now().date()
    # managers = Current_manager.objects.filter(end_date__gte = today_date )
    # traders = Trader.objects.all()
    context = {
            'success':success,
            'failed':failed,
            # 'managers':managers,

    }
    return render(request, 'content/treasury_transactions.html',context)







@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def withdrawings_transactions(request):
    success = failed =0

    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now()
        amount = float(request.POST['amount'])
        notes = request.POST['notes']
        ## get current manager safe
        m_safe = Safe_Month.objects.last()
        ## test amount against trader remaining_money
        manager = Current_manager.objects.filter(user = request.user).first()

        if m_safe.money >= abs(amount)  :
            withdrawings.objects.create(day = date, money_amount = amount, descreption=notes , status = 2 )
            Safe_data.objects.create(day = date, money_amount = -amount, given_person =manager, notes=notes , safe_line_status = 1 )

            m_safe.money -= abs(amount)
            m_safe.save()

            success = 1
        else:
            failed = 1



    context = {
            'success':success,
            'failed':failed,


    }
    return render(request, 'content/withdrawings_transactions.html', context)







@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_single_withdrawing(request):
    success = failed = 0
    cur_m = Current_manager.objects.get(user = request.user)
    all_with = withdrawings.objects.filter(day__date__gte =cur_m.start_date , day__date__lte = cur_m.end_date  ,status = 2 )
    if request.method == "POST":
        money_amount = float(request.POST['money_amount'])
        w_data =  withdrawings.objects.get(id = int(request.POST['witd_id']))
        if money_amount == w_data.money_amount :
            success = 1


            ## update safe
            sm = Safe_Month.objects.last()
            sm.money += w_data.money_amount
            sm.save()

            ## create new safe data entry
            notes  = "نثرية مسترجعة " +  w_data.descreption
            Safe_data.objects.create(day = timezone.now(), money_amount =  w_data.money_amount , given_person = cur_m,
                            notes =notes ,safe_line_status = 1)
            w_data.delete()

        else :
            failed = 1


    context = {
            'all_with' :all_with,
            'success' :success,
            'failed' :failed,
    }
    return render(request, 'content/delete_single_withdrawing.html',context = context)


@login_required
def denied(request):
    return render(request, 'content/denied.html')



@login_required
def change_password(request):

    success = failed = 0
    if request.method == "POST" :
            cur_user = request.user
            userna=cur_user.username

            old_pass = request.POST['password_old']
            new_pass_1 = request.POST['password_new_1']
            new_pass_2 = request.POST['password_new_2']

            ## check old pass
            if cur_user.check_password(old_pass):
                ## check new pass match
                if new_pass_1 == new_pass_2 :
                    cur_user.set_password(new_pass_1)
                    cur_user.save()
                    logout(request)
                    print('username: ' + userna + ' has log out of system at ' + str(datetime.now()))
                    return redirect('content:login-page')
                else :
                    failed = 2
            else:
                failed = 1
    context = {
        'success':success,
        'failed':failed,
    }
    return render(request, "content/change_password.html", context = context)



@login_required
def search_canteen(request):
    products = Product.objects.all()
    # sandwich = Sandwich.objects.all()
    store_product = tpps = all_product_sellings =  None
    data = []
    if request.method == "POST":
        # print(request.POST)
        ## store product
        store_product = Product.objects.get(id = int(request.POST['product_id']))
        ##point products

        all_product_sellings = Point_Product_Sellings.objects.filter(product = store_product, line_type = 0, taken_status = 1)
    if store_product != None :
        data.append(store_product)
    if tpps != None :
        for tpp in tpps:
            data.append(tpp )
        print("# data %d" %(len(data)))

    context = {
        'products':products,
        'store_product':store_product,
        'all_product_sellings':all_product_sellings,

        'data':data,
    }
    return render(request, "content/search_canteen.html", context = context)