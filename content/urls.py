from django.urls import path
from .import views, points_views , trader_views, customers_views, daily_views, product_views, sandwich_views

app_name="content"

urlpatterns = [
    path('', views.home, name='login-page'),
    path('logout/', views.logout_view, name='logout-page'),
    path('login/', views.home, name='login-page'),
    path('change-password/', views.change_password, name='change-password'),
    path('search-canteen/', views.search_canteen, name='search-canteen'),

    path('manager/<int:manager_id>', views.manager, name='manager'),
    path('daily_reports', daily_views.daily_reports, name='daily_reports'),
    path('daily_transaction/', daily_views.daily_transaction, name='daily_transaction'),

    path('denied/', views.denied, name='denied_page'),
    path('treasury_transactions/', views.treasury_transactions, name='treasury_transactions'),
    path('withdrawings_transactions/', views.withdrawings_transactions, name='withdrawings_transactions'),
    path('delete_single_withdrawing/', views.delete_single_withdrawing, name='delete_single_withdrawing'),
    path('store/', views.store, name='store'),
    path('Treasury_receipt/', views.Treasury_receipt, name='Treasury_receipt'),

    path('monthly_receipt/', views.monthly_receipt, name='monthly_receipt'),
    path('withdrawings_all/', views.withdrawings_all, name='withdrawings_all'),



    ##########################################################################################
    ## preoduct views

    path('new_product_type/', product_views.new_product_type, name='new_product_type'),
    path('add_new_mu/', product_views.add_new_mu, name='add_new_mu'),
    path('delete_mu/', product_views.delete_mu, name='delete_mu'),
    path('reduce_product_amount_store/<int:product_id>', product_views.reduce_product_amount_store, name='reduce_product_amount_store'),

    path('update_product/<int:trader_id>', product_views.update_product, name='update_product'),
    path('delete_trader_bill_line/<int:line_id>', product_views.delete_trader_bill_line, name='delete_trader_bill_line'),
    path('edit_trader_bill_line/<int:line_id>', product_views.edit_trader_bill_line, name='edit_trader_bill_line'),
    path('confirm_add_trader_bill/<int:bill_id>', product_views.confirm_add_trader_bill, name='confirm_add_trader_bill'),
    path('product_page/<int:product_id>', product_views.product_page, name='product_page'),



######################################### trader viwes
    path('trader_bill_details/<int:bill_id>', trader_views.trader_bill_details, name='trader_bill_details'),
    path('restore_trader_bill_line/<int:line_id>', trader_views.restore_trader_bill_line, name='restore_trader_bill_line'),
    path('delete_restored_trader_bill_line/<int:line_id>', trader_views.delete_restored_trader_bill_line, name='delete_restored_trader_bill_line'),
    path('edit_restored_trader_bill_line/<int:line_id>', trader_views.edit_restored_trader_bill_line, name='edit_restored_trader_bill_line'),
    path('confirm_restore_trader_bill/<int:bill_id>', trader_views.confirm_restore_trader_bill, name='confirm_restore_trader_bill'),

    path('trader_page/<int:trader_id>', trader_views.trader_page, name='trader_page'),
    path('add_money_dept/<int:trader_id>', trader_views.add_money_dept, name='add_money_dept'),
    path('restore_trader_product_store/<int:trader_id>', trader_views.restore_trader_product_store, name='restore_trader_product_store'),
    path('Debts/', trader_views.Debts, name='Debts'),


    path('give_payment/<int:trader_id>', trader_views.give_payment, name='give_payment'),
    path('add_trader/<int:status>', trader_views.add_trader, name='add_trader'),

################################################################## customer views

    path('customers-page/', customers_views.customers_page, name='customers-page'),
    path('customer-payment/<int:customer_id>', customers_views.customer_payment, name='customer-payment'),
    path('add_customer_dept/<int:customer_id>', customers_views.add_customer_dept, name='add_customer_dept'),
    path('customer-page/<int:customer_id>', customers_views.customer_page, name='customer-page'),
    path('customer-bill-details/<int:bill_id>', customers_views.customer_bill_details, name='customer-bill-details'),
    path('customers-bill-details-page/', customers_views.customer_bill_details_page, name='customers-bill-details-page'),
    path('restore-customer-bill/<int:customer_id>', customers_views.restore_customer_bill, name='restore-customer-bill'),

    # path('confirm-restore-customer-bill/<int:customer_id>', customers_views.confirm_restore_customer_bill, name='confirm-restore-customer-bill'),

    path('restore-customer-bill-line/<int:line_id>', customers_views.restore_customer_bill_line, name='restore-customer-bill-line'),

    # path('customer_give_payment/<int:customer_id>', customers_views.customer_give_payment, name='customer_give_payment'),

    path('customer_all_unpaid_bills/<int:customer_id>', customers_views.customer_all_unpaid_bills, name='customer_all_unpaid_bills'),
    path('customer_all_paid_bills/<int:customer_id>', customers_views.customer_all_paid_bills, name='customer_all_paid_bills'),
    path('customer_all_restored_bills/<int:customer_id>', customers_views.customer_all_restored_bills, name='customer_all_restored_bills'),

    ## coming from customer to point => restord
    path('confirm_restored_customer_bill/<int:bill_id>', customers_views.confirm_restored_customer_bill, name='confirm_restored_customer_bill'),
    path('edit_restored_customer_bill_line/<int:line_id>', customers_views.edit_restored_customer_bill_line, name='edit_restored_customer_bill_line'),
    path('delete_restored_customer_bill_line/<int:line_id>', customers_views.delete_restored_customer_bill_line, name='delete_restored_customer_bill_line'),



#### ########################################################## points views
    path('points/', points_views.points, name='points'),
    path('add_new_point/', points_views.add_new_point, name='add_new_point'),
    path('point_page/<int:point_id>', points_views.point_page, name='point_page'),
    path('edit_selling_price/<int:pp_id>', points_views.edit_selling_price, name='edit_selling_price'),

    path('point_trader_page/<int:point_trader_id>', points_views.point_trader_page, name='point_trader_page'),
    path('add_new_point_bill/', points_views.add_new_point_bill, name='add_new_point_bill'),
    path('add_new_point_seller/', points_views.add_new_point_seller, name='add_new_point_seller'),
    path('add_new_point_payments/<int:point_id>', points_views.add_new_point_payments, name='add_new_point_payments'),
    path('add_new_point_sellings/<int:point_id>', points_views.add_new_point_sellings, name='add_new_point_sellings'),
    path('restore_point_bill_sell/<int:bill_id>', points_views.restore_point_bill_sell, name='restore_point_bill_sell'),
    path('restore_point_product_store/<int:point_id>', points_views.restore_point_product_store, name='restore_point_product_store'),
    path('point_to_point_product/<int:point_id>', points_views.point_to_point_product, name='point_to_point_product'),
    path('point-total-product/<int:tpp>', points_views.point_total_product, name='point-total-product'),

    ## from store to point
    path('confirm_add_point_bill/<int:bill_id>', points_views.confirm_add_point_bill, name='confirm_add_point_bill'),
    path('edit_point_bill_line/<int:line_id>', points_views.edit_point_bill_line, name='edit_point_bill_line'),
    path('delete_point_bill_line/<int:line_id>', points_views.delete_point_bill_line, name='delete_point_bill_line'),

    ## from point to store
    path('confirm_restored_point_bill/<int:point_id>', points_views.confirm_restored_point_bill, name='confirm_restored_point_bill'),
    path('edit_restored_point_bill_line/<int:line_id>', points_views.edit_restored_point_bill_line, name='edit_restored_point_bill_line'),
    path('delete_restored_point_bill_line/<int:line_id>', points_views.delete_restored_point_bill_line, name='delete_restored_point_bill_line'),

    ## from point to point
    path('confirm_point_to_point_bill/<int:point_id>', points_views.confirm_point_to_point_bill, name='confirm_point_to_point_bill'),
    path('edit_point_to_point_bill_line/<int:line_id>', points_views.edit_point_to_point_bill_line, name='edit_point_to_point_bill_line'),
    path('delete_point_to_point_bill_line/<int:line_id>', points_views.delete_point_to_point_bill_line, name='delete_point_to_point_bill_line'),

    ## coming from  point to customer => sellings
    path('confirm_customer_point_bill/<int:bill_id>', points_views.confirm_customer_point_bill, name='confirm_customer_point_bill'),
    path('edit_customer_point_bill_line/<int:line_id>', points_views.edit_customer_point_bill_line, name='edit_customer_point_bill_line'),
    path('delete_customer_point_bill_line/<int:line_id>', points_views.delete_customer_point_bill_line, name='delete_customer_point_bill_line'),





    path('all-discount-bills/', points_views.all_discount_bills, name='all-discount-bills'),



############################################################## sandwiches views

    path('sandwitch/', sandwich_views.sandwitch, name='sandwitch'),
    path('add_sandwich_components/<int:type_id>', sandwich_views.add_sandwich_components, name='add_sandwich_components'),
    path('add_sandwich_component_names/', sandwich_views.add_sandwich_component_names, name='add_sandwich_component_names'),
    path('sand_current_materials/', sandwich_views.sand_current_materials, name='sand_current_materials'),
    path('add_sandwitch/', sandwich_views.add_sandwitch, name='add_sandwitch'),
    path('add_new_sandwitch/', sandwich_views.add_new_sandwitch, name='add_new_sandwitch'),


]
