from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import  Customer, Customer_Bill,Current_manager,Customer_Payment, Safe_data, Safe_Month,  Point_Product_Sellings
from .models import  Point, Trader_Bill, Trader_Product , Point_Product
from django.utils import timezone

@login_required
def customers_page(request):
    customers = Customer.objects.all().order_by("name")
    total_traders_money = total_traders_given = total_traders_remain = 0.0
    # total_traders_money = sum(t.total_money for t in customers)
    # total_traders_given = sum(t.given_money for t in customers)
    total_traders_remain = sum(t.remaining_money for t in customers)


    context = {
        'customers':customers,
        # 'total_customers_money':total_traders_money,
        # 'total_customers_given':total_traders_given,
        'total_customers_remain':total_traders_remain,
    }
    return render(request, 'content/customers.html', context = context)


@login_required
def customer_page(request,customer_id):
    customer = Customer.objects.get(id = customer_id)

    if request.method == "POST" :
        customer.name = request.POST['name']
        customer.address = request.POST['address']
        customer.phone_number = request.POST['phone_number']
        customer.save()

    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 0 , given_status = 1 , bill_type = 0).order_by('-date')
    paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 1 , given_status = 1, bill_type = 0).order_by('-date')
    retunred_bills = Customer_Bill.objects.filter(customer = customer ,paid_status__in=[0,1] , given_status__in = [0,1], bill_type = 1).order_by('-date')

    paid_given_bill = Customer_Payment.objects.filter(g_user = customer, payment_type = 0).order_by('-date')
    restored_paid_bills = Customer_Payment.objects.filter(g_user = customer, payment_type = 1).order_by('-date')

    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'paid_bills':paid_bills,
        'retunred_bills':retunred_bills,

        'paid_given_bill':paid_given_bill,
        'restored_paid_bills':restored_paid_bills,

    }
    return render(request, 'content/customer_page.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_all_unpaid_bills(request,customer_id):
    customer = Customer.objects.get(id = customer_id)

    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 0 , given_status = 1 , bill_type = 0).order_by('date')

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
    totals = [total_bills_cost, bills_total_discount, bills_required_amount,bills_given_amount,bills_remaining_amount   ]


    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'totals':totals,


    }
    return render(request, 'content/customer_all_unpaid_bills.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_all_paid_bills(request,customer_id):
    from_date = to_date = product = un_paid_bills = totals =   None
    customer = Customer.objects.get(id = customer_id)
    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Customer_Bill.objects.filter(customer = customer).first().date.date()

        except:
            from_date = timezone.now().date()

        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()



        un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 1 , given_status = 1 , bill_type = 0 ,
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
        totals = [total_bills_cost, bills_total_discount, bills_required_amount,bills_given_amount,bills_remaining_amount   ]


    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'totals':totals,


    }
    return render(request, 'content/customer_all_paid_bills.html', context)




@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_all_restored_bills(request,customer_id):
    from_date = to_date = product = un_paid_bills = totals =   None
    customer = Customer.objects.get(id = customer_id)
    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Customer_Bill.objects.filter(customer = customer).first().date.date()
        except:
            from_date = timezone.now().date()


        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()



        un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 1 , given_status = 1 , bill_type = 1,
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
        totals = [total_bills_cost, bills_total_discount, bills_required_amount,bills_given_amount,bills_remaining_amount   ]


    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'totals':totals,


    }
    return render(request, 'content/customer_all_restored_bills.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_all_money_bills(request,customer_id):
    from_date = to_date = product = paid_given_bill = totals =   None
    customer = Customer.objects.get(id = customer_id)
    if request.method == "POST":
        try :
            from_date = request.POST['from_date'] if request.POST['from_date'] != "" else Customer_Bill.objects.filter(customer = customer).first().date.date()
        except:
            from_date = timezone.now().date()

        to_date = request.POST['to_date'] if request.POST['to_date'] != "" else timezone.now().date()



        paid_given_bill = Customer_Payment.objects.filter(g_user = customer,    date__date__gte = from_date , date__date__lte = to_date ).order_by('-date')

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
        # totals = [total_bills_cost, bills_total_discount, bills_required_amount,bills_given_amount,bills_remaining_amount   ]


    context = {
        'customer':customer,
        'paid_given_bill':paid_given_bill,
        # 'totals':totals,


    }
    return render(request, 'content/customer_all_money_bills.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_payment(request,customer_id):
    customer = Customer.objects.get(id = customer_id)
    un_paid_bills = customer.customer_unpaid_bill
    failed = success = 0
    if request.method == "POST":
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        # customer = Customer.objects.get(id = int(request.POST['customer_id']))
        amount_loop = amount
        manager = Current_manager.objects.get(user = request.user)
        if (amount + discount) <= customer.remaining_money :
            if discount > 0  :
                remove_discount_from_bills_from_customer(un_paid_bills,discount )

            ## update bills with the given amount
            un_paid_bills = customer.customer_unpaid_bill
            if amount > 0  :
                add_amount_to_bills_from_customer(un_paid_bills, amount )
                ## create new customer  payment

                ## 2. safe_date
                notes = " فاتورة نقدية محصلة من العميل :  " + customer.name
                Safe_data.objects.create(day =  timezone.now(), money_amount = amount, given_person =manager, notes=notes , safe_line_status = 6 )

                m_safe = Safe_Month.objects.last()
                ## m_safe
                m_safe.money +=amount
                m_safe.save()

            if customer.remaining_money == 0 :
                 customer.customer_unpaid_bill.update(paid_status = 1)



            Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                            ,discount = discount, previos_amount =customer.remaining_money + discount + amount, current_amount = customer.remaining_money )

            success = 1

        else :
            failed =1
    un_paid_bills = customer.customer_unpaid_bill
    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'failed':failed ,
        'success':success ,

    }
    return render(request, 'content/customer_payment.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_customer_dept(request,customer_id):
    customer = Customer.objects.get(id = customer_id)
    manager = Current_manager.objects.get(user = request.user)
    if request.method == "POST":
            # print("inside  add customer dept")
            amount = float(request.POST['amount'])
            customer.pre_amount += amount
            customer.save()
            ## 2. safe_date
            notes = request.POST['notes'] +   " \n ملبغ نقدى مدفوع مقدما من العميل " +"\n" + customer.name
            Safe_data.objects.create(day =  timezone.now(), money_amount = amount, given_person =manager, notes=notes , safe_line_status = 6 )

            m_safe = Safe_Month.objects.last()
            ## m_safe
            m_safe.money +=amount
            m_safe.save()
            if amount < 0:
                payment_type = 1
            else :
                payment_type = 0

            Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                            , previos_amount =customer.remaining_money  + amount, current_amount = customer.remaining_money , payment_type = payment_type )

            ## add customer amount to bills
            un_paid_bills = customer.customer_unpaid_bill
            if len(un_paid_bills) > 0 and customer.pre_amount > 0 :
                temp_amount =  customer.pre_amount
                remaining_amount = add_amount_to_bills_from_customer(un_paid_bills, temp_amount )
                customer.pre_amount = remaining_amount
                customer.save()
            if customer.remaining_money == 0:
                customer.customer_unpaid_bill.update(paid_status = 1)

    # print("get to add customer dept")
    return redirect('content:customer-page', customer_id)


def remove_discount_from_bills_from_customer(un_paid_bills, discount ):
    for bill in un_paid_bills:
        ## case 1
        if discount >= bill.remaining_amount:
            temp = bill.remaining_amount
            bill.discount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()

            discount  -= temp
        elif discount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.discount += discount
            bill.save()

            discount = 0

def add_amount_to_bills_from_customer(un_paid_bills, amount ):
    for bill in un_paid_bills:
        ## case 1
        if amount >= bill.remaining_amount:
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()

            amount  -= temp
        elif amount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount += amount
            bill.save()

            amount = 0
        if bill.remaining_amount <= .1:
            bill.paid_status = 1
            bill.save()



    ## remaing amount
    return amount




@login_required
def customer_bill_details(request, bill_id):
    bill = Customer_Bill.objects.get(id = bill_id)
    context = {

        'bill':bill ,

    }

    return render(request, 'content/customer_bill_details.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_customer_bill(request, customer_id):
    customer = Customer.objects.get(id = customer_id)
    customer_bill = None
    if request.method == "POST":
        try :
             customer_bill = Customer_Bill.objects.get(id = int(request.POST['bill_id']) , customer =customer )
        except :
            customer_bill = None
    ## get current restore bill
    cust_cur_res_bill = Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 1 ).last()

    ## get current customer sellings bill
    if cust_cur_res_bill != None and customer_bill == None :
        last_line = cust_cur_res_bill.all_lines.last()
        if last_line != None :
            customer_bill = last_line.come_from.bill

    context = {
        'customer':customer ,
        'bill':customer_bill ,
        'cust_cur_res_bill':cust_cur_res_bill ,

    }

    return render(request, 'content/restore_customer_bill.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_customer_bill_line(request, line_id):
    bill_line = Point_Product_Sellings.objects.get(id = line_id)
    customer_bill = Customer_Bill.objects.get(id = bill_line.bill.id)
    customer = customer_bill.customer
    success = failed = 0

    if request.method == "POST":
        amount = int(request.POST['amount'])
        if amount <= bill_line.total_quantity_sold  :
            restored_bill = create_new_restore_customer_bill(request, customer)
            restore_line   = create_new_restore_line(amount, bill_line, restored_bill)
            success = 1


        else :
            failed = 1




    ## get current restore bill
    cust_cur_res_bill = Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 1 ).last()
    context = {

        'customer':customer_bill.customer ,
        'bill':customer_bill ,
        'success':success ,
        'failed':failed ,
        'cust_cur_res_bill':cust_cur_res_bill ,

    }

    return render(request, 'content/restore_customer_bill.html', context)


def create_new_restore_customer_bill(request, customer):
    ## create new restore bill
    cust_cur_bill = Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 1 ).last()
    if cust_cur_bill == None:
        ## create new one
        print("create new restore bill")
        cur_m = Current_manager.objects.get(user = request.user)
        Customer_Bill.objects.create(customer = customer, manager = cur_m, bill_type = 1)
        cust_cur_bill =  Customer_Bill.objects.filter(given_status = 0, customer = customer, bill_type = 1).last()

    return cust_cur_bill



def create_new_restore_line(amount, bill_line,  restored_bill):
    ## 1. subtract amount from bill line
    bill_line.subtract_from_product(amount , 0)
    ## 2. create new restored line and map it to the restored bill
    quo, rem = divmod(amount , bill_line.quantity_per_packet )
    Point_Product_Sellings.objects.create( date = timezone.now(), quantity = rem , quantity_packet = quo ,
                                            line_type = 1, come_from = bill_line , bill =restored_bill , Point = bill_line.Point,
                                            point_product = bill_line.point_product )





@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def edit_restored_customer_bill_line(request, line_id):
    ## restored bill line
    bill_line = Point_Product_Sellings.objects.get(id = line_id)
    customer_bill = Customer_Bill.objects.get(id = bill_line.bill.id)
    customer = customer_bill.customer

    come_from_bill_line = bill_line.come_from

    new_quantity =  int(request.POST['quantity'])
    new_quantity_packet = int(request.POST['quantity_packet'])

    total_new_q = new_quantity + (new_quantity_packet * come_from_bill_line.quantity_per_packet)
    l_quantity_old = bill_line.total_quantity_sold
    temp_diff = total_new_q - l_quantity_old

    if temp_diff <= come_from_bill_line.total_quantity_sold :
        quo, rem = divmod(total_new_q , come_from_bill_line.quantity_per_packet )
        print("quo %d, rem %d "%(quo, rem))
        bill_line.quantity = rem
        bill_line.quantity_packet = quo
        bill_line.save()

        ## edit origanl come from line
        if temp_diff < 0 :
            come_from_bill_line.add_to_product(abs(temp_diff), 0)

        elif temp_diff > 0 :
            come_from_bill_line.subtract_from_product((temp_diff), 0)


    return redirect('content:restore-customer-bill', customer.id)




@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_restored_customer_bill_line(request, line_id):
    ## restored bill line
    bill_line = Point_Product_Sellings.objects.get(id = line_id)
    customer_bill = Customer_Bill.objects.get(id = bill_line.bill.id)
    customer = customer_bill.customer
    success = failed = 0


    ###  sold bill line created in the sold bill,  delete it
    come_from_bill_line = bill_line.come_from
    come_from_bill_line.add_to_product(bill_line.total_quantity_sold , 0)

    bill_line.delete()



    return redirect('content:restore-customer-bill', customer.id)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_restored_customer_bill(request, bill_id):
    add_to_customer_flag = amount = 0
    notes = ""
    manager = Current_manager.objects.get(user = request.user)
    customer_bill = Customer_Bill.objects.get(id = bill_id)
    customer_bill.given_status = 1
    customer_bill.paid_status = 1
    customer_bill.save()

    ## update point with the restored amount
    for line in customer_bill.all_lines :
        line.point_product.add_to_product(line.quantity , line.quantity_packet)

    customer = customer_bill.customer

    ## check if the main  bill is already paid or not
    customer_main_bill =  customer_bill.all_lines.last().come_from.bill
    if customer_main_bill.paid_status == 1:
        customer.pre_amount += customer_bill.required_amount

        customer.save()
        notes += " فاتورة مسترجعة من العميل "
        amount =customer_bill.required_amount

        Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = -amount
                        , previos_amount =customer.remaining_money + amount, current_amount = customer.remaining_money , payment_type = 1, notes = notes)

    ## if it not a paid bill but the remaining amount is less than or equal 0 <= 0
    else :
        if customer_main_bill.remaining_amount <= 0 :
            customer.pre_amount += abs(customer_main_bill.remaining_amount)
            customer_main_bill.paid_status = 1
            customer_main_bill.save()
            customer.save()


        notes += " فاتورة مسترجعة من العميل "
        amount = abs(customer_bill.required_amount)

        Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = -amount
                        , previos_amount =customer.remaining_money + amount, current_amount = customer.remaining_money , payment_type = 1, notes = notes)






    return redirect('content:restore-customer-bill', customer.id)

def restore_product_to_points(customer_bill):
    bill_lines = customer_bill.all_lines


    ## get bills cost buy
    customer_bill_cost_buy = sum(line.money_quantity_buy for line in bill_lines)
    total_bill_required = sum(line.required_amount for line in bill_lines)
    ##get month_tc


    ## get bills cost sell
    customer_bill_cost_sell = sum(line.required_amount for line in bill_lines)
    ##get month_tc
    customer = customer_bill.customer
    customer.total_money -= customer_bill_cost_sell
    customer.save()





@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_give_payment(request, customer_id):
    customer = Customer.objects.get(id = customer_id)
    failed = success = 0
    if request.method == "POST":
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        # customer = Customer.objects.get(id = int(request.POST['customer_id']))
        amount_loop = amount
        m_safe = Safe_Month.objects.last()
        if  (amount + discount ) <= (customer.remaining_money * -1) and  m_safe.money >= amount :
            restored_bills = get_customer_restored_bills(customer)
            if discount > 0 :
                remove_discount_from_restored_bills(restored_bills, discount)

            restored_bills = get_customer_restored_bills(customer)
            if amount > 0  :
                remove_given_amount_from_restored_bills(restored_bills, amount )
                ## create new customer  payment
                manager = Current_manager.objects.get(user = request.user)
                Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                                ,discount = discount, previos_amount = customer.remaining_money , current_amount = customer.remaining_money +( discount + amount)  , payment_type = 1)

                ## 2. safe_date
                notes = " فاتورة نقدية مدفوعة لصالح العميل : " + customer.name
                Safe_data.objects.create(day =  timezone.now(), money_amount = -amount, given_person =manager, notes=notes , safe_line_status = 7 )

                m_safe = Safe_Month.objects.last()
                ## m_safe
                m_safe.money -= amount
                m_safe.save()

            #

            ## update customer given - remaining_money
            customer.given_money -= amount
            customer.total_money += discount
            customer.normalize()


            success = 1

        else :
            failed =1

    context = {
        'customer':customer,
        'success':success ,
        'failed':failed ,
    }
    return render(request, 'content/customer_give_payment.html', context)


def get_customer_restored_bills(customer):
    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,bill_type = 0, given_status = 1)
    result = []
    # result.append(bill for bill in un_paid_bills if bill.remaining_amount < 0 )
    for bill in un_paid_bills:
        if bill.remaining_amount < 0:
            result.append(bill)

    # for bill in result :
    #     print(" unpaind  id %d" %(bill.id) )
    return result

def remove_discount_from_restored_bills(un_paid_bills, discount ):
    for bill in un_paid_bills:
        ## case 1
        if discount >= (bill.remaining_amount * -1):
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount ## here reaming amount is negative
            bill.paid_status = 1
            bill.save()

            discount  -= (temp * -1)
        elif discount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount -= discount
            bill.save()

            discount = 0

def remove_given_amount_from_restored_bills(un_paid_bills, amount ):
    for bill in un_paid_bills:
        ## case 1
        if amount >= (-1 * bill.remaining_amount ):
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount  ## here reaming amount is negative
            bill.paid_status = 1
            bill.save()

            amount  -= ( temp * -1)
        elif amount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount += amount
            bill.save()

            amount = 0
        if bill.remaining_amount <= .01:
            bill.paid_status = 1
            bill.save()





@login_required
def customer_bill_details_page(request):
    bill = None
    bill_type = -1
    ## in case of trader bill
    data = []

    if request.method == "POST":
        bill_type = int(request.POST['bill_type'])

        try:
            if bill_type == 0 : # customer bill
                bill = Customer_Bill.objects.get(id = int(request.POST['bill_id']) )
            elif bill_type == 1: #trader bill
                print("find items")
                bill = Trader_Bill.objects.get(id = int(request.POST['bill_id']) )

                ## get all bill lines first and for each line =>

                for line in  bill.all_lines :
                    single_item = []
                    ## we need four sections for this type of bills
                    ##1. product in store
                    single_item.append(line)
                    ## 2. point product

                    single_item.append(Point_Product.objects.filter(trader_product = line))
                    ## 3. customer payments
                    single_item.append(Point_Product_Sellings.objects.filter(point_product__trader_product = line, line_type = 0).order_by("-id"))
                    print("number of sold lines %d" %len(single_item[2]))
                    ##4. restored to trader
                    single_item.append(Trader_Product.objects.filter(come_from = line, line_type = 1).order_by("-id"))
                    data.append(single_item)
                    single_item = []
                    print("find items")



        except :
            bill = None


    context = {
        'bill' : bill,
        'bill_type' : bill_type,
        'data' : data,
    }

    return render(request,"content/customer_bill_details_page.html", context = context)



#########################
