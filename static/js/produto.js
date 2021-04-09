// some scripts

// jquery ready start

const CAPA = document.getElementById("capa");

$(document).ready(function() {

    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });

    $(document).on('click', '.image-preview', function (e) {
        // console.log($(this).attr("id"));
        var name = $(this).attr("id");
        console.log(name + " was clicked!");

        CAPA.src = $(this).children()[0].src;
    });

	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
		$('[data-toggle="tooltip"]').tooltip()
	} // end if

}); 
// jquery end

