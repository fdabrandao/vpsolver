$(document).ready(function(){
    $("#examples").change(function() {
        document.location.href = $(this).val();
    });
});
