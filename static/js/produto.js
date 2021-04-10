// some scripts

// jquery ready start

const DSPL = document.getElementById("button-display");
const CAPA = document.getElementById("capa");

$(document).ready(function() {

    $(document).on('click', '.image-preview', function (e) {
        // console.log($(this).attr("id"));
        var name = $(this).attr("id");
        console.log(name + " was clicked!");

        CAPA.src = $(this).children()[0].src;
    });

    $(document).on('click', '.btn-outline-primary, .btn-primary', function (e) {

        const thisid = $(this).attr("id");

        $.ajax({
            url: '/add-to-cart',
            type: 'POST',
            data: '{"qtd": "' + DSPL.value + '", "pid": "' + $(this).attr("value") + '"}', 
            success: function (response) {

                CART.innerHTML = "" + response + " itens";
                if (thisid === "btn-buy")
                    window.location.href = "/carrinho";

            }
        });

    });

}); 
// jquery end

