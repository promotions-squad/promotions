$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_productid").val(res.productid);
        $("#promotion_category").val(res.category);
        if (res.available == true) {
            $("#promotion_available").val("true");
        } else {
            $("#promotion_available").val("false");
        }
        $("#promotion_discount").val(res.discount);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_productid").val("");
        $("#promotion_category").val("");
        $("#promotion_available").val("");
        $("#promotion_discount").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        var productid = $("#promotion_productid").val();
        var category = $("#promotion_category").val();
        var available = $("#promotion_available").val() == "true";
        var discount = $("#promotion_discount").val();

        var data = {
            "productid": productid,
            "category": category,
            "available": available,
            "discount": discount
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        var promotion_id = $("#promotion_id").val();
        var productid = $("#promotion_productid").val();
        var category = $("#promotion_category").val();
        var available = $("#promotion_available").val() == "true";
        var discount = $("#promotion_discount").val();

        var data = {
            "productid": productid,
            "category": category,
            "available": available,
            "discount": discount
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/promotions/" + promotion_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Cancel a Promotion
    // ****************************************

    $("#cancel-btn").click(function () {

        var promotion_id = $("#promotion_id").val();


        var ajax = $.ajax({
                type: "PUT",
                url: "/promotions/" + promotion_id + "/cancel",
                contentType:"application/json"
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        var promotion_id = $("#promotion_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions/" + promotion_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        var promotion_id = $("#promotion_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/promotions/" + promotion_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        var productid = $("#promotion_productid").val();
        var category = $("#promotion_category").val();
        var available = $("#promotion_available").val() == "true";
        var discount = $("#promotion_discount").val();

        var queryString = ""

        if (productid) {
            queryString += 'productid=' + productid
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }
        if (discount) {
            if (queryString.length > 0) {
                queryString += '&discount=' + discount
            } else {
                queryString += 'discount=' + discount
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:20%">ProductID</th>'
            header += '<th style="width:20%">Category</th>'
            header += '<th style="width:20%">Available</th>'
            header += '<th style="width:20%">Discount</th></tr>'
            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                var promotion = res[i];
                var row = "<tr><td>"+promotion.id+"</td><td>"+promotion.productid+"</td><td>"+promotion.category+"</td><td>"+promotion.available+"</td><td>"+promotion.discount+"</td></tr>";
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
