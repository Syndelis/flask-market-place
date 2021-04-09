// some scripts

// jquery ready start

const AZ = document.getElementById("A-Z");
const ZA = document.getElementById("Z-A");
const PU = document.getElementById("Preço+");
const PD = document.getElementById("Preço-");

$(document).ready(function() {

    $(document).on('click', '.smart-checkbox', function (e) {

        var name = $(this).attr("id");

        if ($(this).is(':checked')) {
            if      (name === "A-Z")    ZA.checked = false;
            else if (name === "Z-A")    AZ.checked = false;
            else if (name === "Preço+") PD.checked = false;
            else if (name === "Preço-") PU.checked = false;
        }
    });

    $(document).on('click', '.btn-outline-primary', function (e) {

        $.ajax({
            url: '/add-to-cart',
            type: 'POST',
            data: '{"qtd": "1", "pid": "' + $(this).attr("value") + '"}', 
            success: function (response) {
                CART.innerHTML = "" + response + " itens";
            }
        });

    });

});