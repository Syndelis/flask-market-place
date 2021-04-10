$(document).ready(function() {

    $(document).on('click', '.btn-light', function (e) {

        // - and + buttons
        if ($(this).attr("type") === "button") {

            const el = $(this).parent().parent().find("input.form-control");
            const op = ($(this).attr("id") === "button-plus" ? 1 : -1)
            
            el.attr("value", Math.max(1, Number(el.attr("value"))+op));

        }

        // × button
        else {

        }

    });

});