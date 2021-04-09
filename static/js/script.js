// some scripts

// jquery ready start

const AZ = document.getElementById("A-Z");
const ZA = document.getElementById("Z-A");
const PU = document.getElementById("Preço+");
const PD = document.getElementById("Preço-");

$(document).ready(function() {
	// jQuery code


    /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
    For sliders, interactions and other

    */ ///////////////////////////////////////
    

	//////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });

    $(document).on('click', '.smart-checkbox', function (e) {
        // console.log($(this).attr("id"));
        var name = $(this).attr("id");

        if ($(this).is(':checked')) {
            if      (name === "A-Z")    ZA.checked = false;
            else if (name === "Z-A")    AZ.checked = false;
            else if (name === "Preço+") PD.checked = false;
            else if (name === "Preço-") PU.checked = false;
        }
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');

        } else {
            item.removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });


    // $('.js-check :checkbox').change(function () {
    //     console.log('here!')
    //     var check_attr_name = $(this).attr('name');
    //     if ($(this).is(':checked')) {
    //         $(this).closest('.js-check').addClass('active');
    //        // item.find('.radio').find('span').text('Add');
    //     } else {
    //         $(this).closest('.js-check').removeClass('active');
    //         // item.find('.radio').find('span').text('Unselect');
    //     }
    // });



	//////////////////////// Bootstrap tooltip
	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
		$('[data-toggle="tooltip"]').tooltip()
	} // end if




    
}); 
// jquery end

