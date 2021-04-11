// some scripts

// jquery ready start

$(document).ready(function() {

    $(document).on('click', '.item-thumb', function (e) {

        const url = $(this).children().eq(0).attr("src");
        $(this).remove();

        $.ajax({
            url: '/remove-image',
            type: 'POST',
            data: url, 
            success: function (response) {}
        });

    });

}); 
// jquery end

