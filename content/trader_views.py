from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product,  Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings
from .models import Trader_Bill, Customer

from django.utils import timezone
from django.db.models import Sum,Q
from getmac import get_mac_address as gma
Computer_Mac_Address = '5C:b9:01:43:f1:28'

@login_required
def Debts(request):
    traders = Trader.objects.all().order_by("name")
    total_traders_money = total_traders_given = total_traders_remain = 0.0
    total_traders_money = sum(t.total_money for t in traders)
    total_traders_given = sum(t.given_money for t in traders)
    total_traders_remain = sum(t.remaining_money for t in traders)
    ## if it is not a manager user
    ## then remove manager trader
    if request.user.groups.filter(name = "managers").count() == 0:
        traders = traders.exclude(name="السيد مدير المنطقة")

    context = {
        'traders':traders,
        'total_traders_money':total_traders_money,
        'total_traders_given':total_traders_given,
        'total_traders_remain':total_traders_remain,
    }
    return render(request, 'content/Debts.html', context = context)

@login_required
def trader_page(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    trader_products_names = set()
    manager_money = 0.0

    if request.method == "POST" :
        trader.name = request.POST['name']
        trader.address = request.POST['address']
        trader.phone_number = request.POST['phone_number']
        trader.save()


    if trader.name == "السيد مدير المنطقة":
            pass
    else:
        tps = Trader_Product.objects.filter(trader = trader).values_list('product').distinct()


        for tp in tps:
                trader_products_names.add(Product.objects.get(id = tp[0]))

    trader_pills = Trader_Payment.objects.filter(reciever = trader).order_by('-date')
    trader_transactions = Trader_Bill.objects.filter(trader = trader, bill_type = 0, given_status = 1).order_by('-date')
    trader_restores = Trader_Bill.objects.filter(trader = trader, bill_type = 1, given_status = 1).order_by('-date')
    # if trader.name == "السيد مدير المنطقة":
    #     manager_money = sum(t.total_cost for tt in trader_transactions )
    context = {
        'trader_pdata':trader,
        'trader_products':trader_products_names,
        'trader_pills':trader_pills,
        'trader_transactions':trader_transactions,
        'trader_restores':trader_restores,
        # 'manager_money':manager_money,
    }
    return render(request, 'content/trader_page.html', context)




@login_required
def trader_all_unpaid_bills(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    from_date = to_date = product = un_paid_bills = totals =   None

    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Trader_Bill.objects.filter(trader = trader).first().date.date()
        except:
            from_date = timezone.now().date()

        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()

        un_paid_bills = Trader_Bill.objects.filter(trader = trader, bill_type = 0, given_status = 1 , paid_status = 0,
                                        date__date__gte = from_date , date__date__lte = to_date ).order_by('-date')
        total_bills_cost = round( sum( t.total_bill_cost for t in un_paid_bills), 1 ) ### 0
        lls_add_discount = round( sum( t.discount for t in un_paid_bills), 1 )     ### 3
        bills_total_discount = round( sum( t.total_discount for t in un_paid_bills), 1 )     ### 4
        #
        #
        bills_required_amount = round( sum( t.required_amount for t in un_paid_bills), 1 )  ### 5
        # bills_restored_amount_cost_ad = round( sum( t.restored_amount_cost_ad for t in un_paid_bills), 1 )  ### 6
        #
        bills_given_amount = round( sum( t.given_amount for t in un_paid_bills), 1 )     ### 7
        bills_remaining_amount = round( sum( t.remaining_amount for t in un_paid_bills), 1 )     ### 8
        #
        totals = [trader.total_money + bills_total_discount , bills_total_discount, trader.total_money ,trader.given_money ,trader.remaining_money   ]

    context = {
        'trader':trader,
        'un_paid_bills':un_paid_bills,
        'totals':totals,

    }
    return render(request, 'content/trader_all_unpaid_bills.html', context)


@login_required
def trader_all_paid_bills(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    from_date = to_date = product = paid_bills = totals =   None

    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Trader_Bill.objects.filter(trader = trader).first().date.date()
        except:
            from_date = timezone.now().date()

        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()

        paid_bills = Trader_Bill.objects.filter(trader = trader, bill_type = 0, given_status = 1 , paid_status = 1,
                                        date__date__gte = from_date , date__date__lte = to_date ).order_by('-date')
        if len(paid_bills) > 0:
            total_bills_cost = round( sum( t.total_bill_cost for t in paid_bills), 1 ) ### 0
            lls_add_discount = round( sum( t.discount for t in paid_bills), 1 )     ### 3
            bills_total_discount = round( sum( t.total_discount for t in paid_bills), 1 )     ### 4
            #
            #
            bills_required_amount = round( sum( t.required_amount for t in paid_bills), 1 )  ### 5
            # bills_restored_amount_cost_ad = round( sum( t.restored_amount_cost_ad for t in un_paid_bills), 1 )  ### 6
            #
            bills_given_amount = round( sum( t.given_amount for t in paid_bills), 1 )     ### 7
            bills_remaining_amount = round( sum( t.remaining_amount for t in paid_bills), 1 )     ### 8
            #
            totals = [trader.total_money + bills_total_discount , bills_total_discount, trader.total_money ,trader.given_money ,trader.remaining_money   ]

    context = {
        'trader':trader,
        'paid_bills':paid_bills,
        'totals':totals,

    }
    return render(request, 'content/trader_all_paid_bills.html', context)



@login_required
def trader_all_restored_bills(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    from_date = to_date = product = un_paid_bills = totals =   None

    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Trader_Bill.objects.filter(trader = trader).first().date.date()
        except:
            from_date = timezone.now().date()

        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()

        un_paid_bills = Trader_Bill.objects.filter(trader = trader, bill_type = 1, given_status = 1 ,
                                        date__date__gte = from_date , date__date__lte = to_date ).order_by('-date')
        total_bills_cost = round( sum( t.total_bill_cost for t in un_paid_bills), 1 ) ### 0
        lls_add_discount = round( sum( t.discount for t in un_paid_bills), 1 )     ### 3
        bills_total_discount = round( sum( t.total_discount for t in un_paid_bills), 1 )     ### 4
        #
        #
        bills_required_amount = round( sum( t.required_amount for t in un_paid_bills), 1 )  ### 5
        # bills_restored_amount_cost_ad = round( sum( t.restored_amount_cost_ad for t in un_paid_bills), 1 )  ### 6
        #
        bills_given_amount = round( sum( t.given_amount for t in un_paid_bills), 1 )     ### 7
        bills_remaining_amount = round( sum( t.remaining_amount for t in un_paid_bills), 1 )     ### 8
        #
        totals = [trader.total_money + bills_total_discount , bills_total_discount, trader.total_money ,trader.given_money ,trader.remaining_money   ]

    context = {
        'trader':trader,
        'un_paid_bills':un_paid_bills,
        # 'totals':totals,

    }
    return render(request, 'content/trader_all_restored_bills.html', context)


@login_required
def trader_all_money_bills(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    from_date = to_date = product = trader_pills = totals =   None

    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Trader_Payment.objects.filter(reciever = trader).first().date.date()
        except :
            from_date = timezone.now().date()
        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()

        trader_pills = Trader_Payment.objects.filter(reciever = trader,
                                        date__date__gte = from_date , date__date__lte = to_date ).order_by('-date')
        # total_bills_cost = round( sum( t.total_bill_cost for t in un_paid_bills), 1 ) ### 0
        # lls_add_discount = round( sum( t.discount for t in un_paid_bills), 1 )     ### 3
        # bills_total_discount = round( sum( t.total_discount for t in un_paid_bills), 1 )     ### 4
        # #
        # #
        # bills_required_amount = round( sum( t.required_amount for t in un_paid_bills), 1 )  ### 5
        # # bills_restored_amount_cost_ad = round( sum( t.restored_amount_cost_ad for t in un_paid_bills), 1 )  ### 6
        # #
        # bills_given_amount = round( sum( t.given_amount for t in un_paid_bills), 1 )     ### 7
        # bills_remaining_amount = round( sum( t.remaining_amount for t in un_paid_bills), 1 )     ### 8
        # #
        # totals = [trader.total_money + bills_total_discount , bills_total_discount, trader.total_money ,trader.given_money ,trader.remaining_money   ]

    context = {
        'trader':trader,
        'trader_pills':trader_pills,
        # 'totals':totals,

    }
    return render(request, 'content/trader_all_money_bills.html', context)






@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0 and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def trader_bill_details(request, bill_id):
    bill = Trader_Bill.objects.get(id = bill_id)

    context = {
        'current_bill':bill,

    }
    return render(request, 'content/trader_bill_details.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0  and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def add_trader(request, status):
    success = failed = 0

    if request.method == "POST":
        date = request.POST['date']
        name = request.POST['name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']

        if status == 0 : ## add trader
            ## check tyhat product is not in the database i.e not in the store  ---> a new product really
            try:
                prod = Trader.objects.get(name = name)
                ## if success failed = 1
                failed = 1
                print("existing trader")

            except :
                success = 1
                print("new trader")
                Trader.objects.create(name = name , date = date, address = address,phone_number  = phone_number )

        elif status == 1:  ## add customer
            ## check tyhat product is not in the database i.e not in the store  ---> a new product really
            try:
                prod = Customer.objects.get(name = name)
                ## if success failed = 1
                failed = 1
                print("existing product")

            except :
                success = 1
                print("new customer")
                Customer.objects.create(name = name , date = date, address = address,phone_number  = phone_number )




    context = {
            'success':success,
            'failed':failed,
            'status':status,

        }
    return render(request, 'content/add_trader.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0  and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def give_payment(request,trader_id):
    success = failed =total_safe =trader_remainings=  0
    trader = Trader.objects.get(id = trader_id)
    trader_bills = Trader_Bill.objects.filter(trader = trader,paid_status = 0, bill_type = 0).order_by('-id')
    total_bill = 0
    for bill in trader_bills :
        total_bill += bill.remaining_amount
    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now()
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        amount_loop = amount
        manager = Current_manager.objects.get(user = request.user)
        notes = request.POST['notes']
        # bill_file = request.FILES['bill_file']
        ## get current manager safe
        m_safe = Safe_Month.objects.last()

        if trader.remaining_money >= (amount + discount) and m_safe.money >= amount  and (amount + discount) > 0 :
            if discount > 0:
                remove_discount_from_bills_from_trader(trader_bills, discount)
            if amount > 0:
                trader_bills = Trader_Bill.objects.filter(trader = trader,paid_status = 0, bill_type = 0).order_by('-id')
                add_amount_to_bills_from_trader(trader_bills, amount)

            ## update trader , safe _ total safe
            trader.total_money -= discount
            trader.given_money += amount

            ### zeroing trader money
            if trader.remaining_money <= .99:
                trader.given_money= 0
                trader.total_money = 0


            trader.save()
            ## this is a special case , occurring when we restore products to trader again
            ## we do not subtract from old bills  , and we create new return back bills so this extra amount of money occurs
            ## this is caused due to returned bills
            if trader.remaining_money == 0:
                 Trader_Bill.objects.filter(trader = trader,paid_status = 0, bill_type = 0).update(paid_status = 1)

            m_safe.money -= amount
            m_safe.save()

            ## create new bill
            notes +=" -- اسم التاجر -- "+trader.name
            previos_amount = trader.remaining_money + discount + amount
            Trader_Payment.objects.create(date = date, discount = discount, amount = amount, reciever = trader , sender= manager, notes=notes
                                         , previos_amount = previos_amount , current_amount = trader.remaining_money    )
            ## create new treasure entry
            if amount > 0:
                Safe_data.objects.create(day = date, money_amount = -amount, given_person =manager, notes=notes, safe_line_status = 3 )




            success = 1
        else:
            failed = 1
            if trader.remaining_money < amount:
                trader_remainings = trader.remaining_money
            elif m_safe.money < amount:
                total_safe = m_safe.money

    today_date =  timezone.now().date()
    managers = Current_manager.objects.filter(end_date__gte = today_date )

    trader_bills = Trader_Bill.objects.filter(trader = trader,paid_status = 0, bill_type = 0).order_by('-id')
    total_bill = 0
    for bill in trader_bills :
        total_bill += bill.remaining_amount
    context = {
            'success':success,
            'failed':failed,
            'bills':trader_bills,
            # 'managers':managers,
            'total_safe':total_safe,
            'trader_remainings':trader_remainings,
            'total_bill':total_bill,
            'trader':trader,
    }
    return render(request, 'content/give_payment.html',context)

def remove_discount_from_bills_from_trader(bills,  discount):
    for bill in bills :
        if discount >= bill.remaining_amount:
            discount -=  bill.remaining_amount
            bill.discount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()
        ## amount < bill.cost or amount = 0
        ## create new bill with the remaing money and make old given =1
        elif discount > 0:
            ## create new one
            # Trader_Product.objects.create(product = bill.product ,manager =bill.manager ,trader = trader, total_cost = amount_loop, total_cost_old = amount_loop, date=date,given_status =1)
            bill.discount += discount
            bill.save()
            discount = 0
            break

def add_amount_to_bills_from_trader(bills,  amount):
    for bill in bills :
        if amount >= bill.remaining_amount:
            amount -=  bill.remaining_amount
            bill.given_amount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()
        ## amount < bill.cost or amount = 0
        ## create new bill with the remaing money and make old given =1
        elif amount > 0:
            ## create new one
            # Trader_Product.objects.create(product = bill.product ,manager =bill.manager ,trader = trader, total_cost = amount_loop, total_cost_old = amount_loop, date=date,given_status =1)
            bill.given_amount += amount
            bill.save()
            amount = 0
            break

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0  and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def restore_trader_product_store(request , trader_id):
    trader = Trader.objects.get(id = trader_id)
    manager = Current_manager.objects.get(user = request.user)
    trader_bills = Trader_Bill.objects.filter(trader = trader, bill_type = 0, given_status = 1).order_by('-date')
    tb =[]
    for b in trader_bills:
        if b.has_any_quantity_in_store:
            tb.append(b)
    trader_bills = tb

    failed = success = 0
    ## get current restored bill
    try :
        crb = Trader_Bill.objects.get(manager = manager, trader = trader , given_status = 0, bill_type = 1)

        ctb = Trader_Bill.objects.get(id = crb.get_any_line.come_from.trader_bill.id)

    except :
         ctb = crb = None




    context = {
            'trader':trader,
            # 'products':products,
            'trader_bills':trader_bills,
            'success':success,
            'failed':failed,
            'ctb':ctb,
            'crb':crb,

        }
    return render(request, 'content/restore_trader_product_store.html',context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0 and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def restore_trader_bill_line(request, line_id):
    manager = Current_manager.objects.get(user = request.user)
    line = Trader_Product.objects.get(id = line_id)
    trader = line.trader
    ## 1. create current restore bill
    try :
        ctb = Trader_Bill.objects.get(manager = manager, trader = trader , given_status = 0, bill_type = 1)

    except :
         Trader_Bill.objects.create( manager = manager, trader = trader , given_status = 0, bill_type = 1)
         ctb = Trader_Bill.objects.get(manager = manager,trader = trader , given_status = 0, bill_type = 1)


    ##2. create restore line with refercing to the line_id
    try :
        crl = Trader_Product.objects.get( trader_bill= ctb, come_from = line , given_status = 0 , line_type = 1 )

    except :
         Trader_Product.objects.create( trader_bill= ctb, come_from = line , given_status = 0 , line_type = 1, total_quantity_fixed = line.total_quantity_fixed
                                        , quantity_per_packet = line.quantity_per_packet, packet_price = line.packet_price, discount_per_packet = line.discount_per_packet )
         crl = Trader_Product.objects.get(trader_bill= ctb, come_from = line , given_status = 0 , line_type = 1)

    ## 3. check amount
    amount = int(request.POST['amount'])
    if amount <= line.total_quantity_in_store :
        ##3.1 subtract from original line
        line.subtract_from_product(amount,0)
        line.restored_quantity += amount
        line.save()

        ### 3.2 add tom crl
        crl.add_to_product(amount, 0)




    return redirect("content:restore_trader_product_store", trader.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0 and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def delete_restored_trader_bill_line(request, line_id):
    line = Trader_Product.objects.get(id = line_id)
    trader = line.come_from.trader

    ## restore amount to come from line and edit restord quantity
    line.come_from.add_to_product(line.quantity, line.quantity_packet)
    line.come_from.restored_quantity -= line.total_quantity
    line.come_from.save()

    line.delete()

    return redirect('content:restore_trader_product_store', trader.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0  and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def edit_restored_trader_bill_line(request, line_id):
    # print(request.POST) ## this is a restored line
    line = Trader_Product.objects.get(id = line_id)
    new_quantity =  int(request.POST['quantity'])
    new_quantity_packet = int(request.POST['quantity_packet'])

    total_new_q = new_quantity + (new_quantity_packet * line.come_from.quantity_per_packet)
    l_quantity_old = line.total_quantity
    temp_diff = total_new_q - l_quantity_old

    if temp_diff <= line.come_from.total_quantity_in_store and temp_diff != 0:
        line.quantity =new_quantity
        line.quantity_packet =new_quantity_packet
        line.save()

        ## edit origanl come from line
        if temp_diff < 0 :
            line.come_from.add_to_product(abs(temp_diff), 0)
            line.come_from.restored_quantity += temp_diff
            line.come_from.save()

        elif temp_diff > 0 :
            line.come_from.subtract_from_product((temp_diff), 0)
            line.come_from.restored_quantity +=  temp_diff
            line.come_from.save()




    return redirect('content:restore_trader_product_store', line.come_from.trader.id)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0  and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def confirm_restore_trader_bill(request, bill_id):


    bill = Trader_Bill.objects.get(id = bill_id)
    given_money_amount = float(request.POST['given_money_amount'])
    discount = float(request.POST['discount'])
    ## get current manager safe
    m_safe = Safe_Month.objects.last()
    manager = Current_manager.objects.get(user = request.user)
    if (given_money_amount + discount) == bill.required_amount : #and m_safe.money >= given_money_amount:
        ##1. update bill
        try :
            bill.bill_file = request.FILES['bill_file']
        except  :
            bill.bill_file  = None
        bill.given_amount += given_money_amount
        bill.discount += discount
        bill.notes = request.POST['notes']
        bill.given_status = 1
        bill.all_lines.update(given_status = 1)
        #if (given_money_amount + discount) == bill.required_amount :
        bill.paid_status = 1
        bill.save()

        ##2. update trader
        trader = bill.trader
        trader.total_money -= given_money_amount
        #trader.given_money += given_money_amount
        trader.save()

    return redirect('content:restore_trader_product_store', bill.trader.id)




@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0  and  Computer_Mac_Address.lower() == gma().lower(), login_url='content:denied_page')
def add_money_dept(request,trader_id):
    failed = success = 0
    trader = Trader.objects.get(id = trader_id)
    cur_m = Current_manager.objects.get(user = request.user)
    if request.method == "POST":
        amount = float(request.POST['amount'])
        notes  = request.POST['notes']
        # Trader_Product.objects.create(total_cost = amount , total_cost_old = amount,given_status = 0,trader = trader,
        #         manager = cur_m  ,notes =notes   )

        trader.total_money += amount

        trader.save()


        ## update safe and safe data
        sfm = Safe_Month.objects.last()
        sfm.money += amount
        sfm.save()
        notes += " وارد من التاجر : " + trader.name
        Safe_data.objects.create(day = timezone.now(), money_amount = amount ,given_person =cur_m ,
                notes = notes, safe_line_status =6)

        previos_amount = trader.remaining_money - amount
        Trader_Payment.objects.create(date = timezone.now(), amount = amount, reciever = trader , sender= cur_m, notes=notes
                                     , previos_amount = previos_amount , current_amount = trader.remaining_money , payment_type = 1   )

        success = 1






    context = {
        "trader":trader,
        "success":success,
    }
    return render(request, 'content/add_money_dept.html',context)
