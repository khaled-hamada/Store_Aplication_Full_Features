divlist = $("div[id^='sell_product']");
divlist.hide();
divlist_2 = $("div[id^='sell_product_bills_']");
divlist_2.hide();
$(document).ready(function(){
  //  ^ means sta
  divlist = $("div[id^='sell_product']");
  divlist.hide();
  divlist_2 = $("div[id^='sell_product_bills_']");
  divlist_2.hide();

  // var cur_product = $("#search_list").find("option:selected").attr("value");
  $("#search_list").change(function(){

      $(this).find("option:selected").each(function(){
        //console.log("change product list");
          var optionValue = $(this).attr("value");
          divlist = $("div[id^='sell_product']");
          divlist.hide();
          $("#sell_product_"+optionValue).show();
          //console.log("#sell_product_"+optionValue);

          // cur_product = $("#search_list").find("option:selected").attr("value");


          //   next select which drop down list

          divlist_2 = $("div[id^='sell_product_bills']");
          divlist_2.hide();

          $("#search_list_bills_"+optionValue).change(function(){

            // console.log("change search list");
              $(this).find("option:selected").each(function(){
                  var optionValue_2= $(this).attr("value");

                  divlist_3 = $("div[id^='sell_product_bills']");
                  divlist_3.hide();
                  $("#sell_product_bills_"+optionValue_2).show();
                  console.log("#sell_product_bills_"+optionValue_2);


              });
          }).change();




      });

  }).change();


//
//   $('#search_list_bills').on('change', function() {
//   alert( this.value );
// });

          //  hide sub_product div at start
          // $("#sub_product_div").hide();
          // $("#sub_product_div :input").attr('required', false);
          $("#toggle").click(function(){

               if($("#toggle").text() == "إخفاء"){
                 $("#toggle").text("إظهار");
                 $("#sub_product_div").hide();
                 $("#sub_product_div :input").attr('required', false);
                 // $("#sub_product_div :input").hide();
               }
               else{
                 $("#toggle").text("إخفاء");
                 $("#sub_product_div").show();
                $("#sub_product_div :input").attr('required', true);
                  // $("#sub_product_div :input").show();
               }

               // $('.required').prop('required', function(){
               //   return  $(this).is(':visible');
               // });

            });



  });
