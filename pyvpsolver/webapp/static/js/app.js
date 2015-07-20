$(document).ready(function(){
    $("#examples").change(function() {
        document.location.href = $(this).val();
    });

    $("#input").keydown(function(e) {
        if (e.keyCode === 9) { // tab was pressed
            // get caret position/selection
            var val = this.value,
                start = this.selectionStart,
                end = this.selectionEnd;

            // set textarea value to: text before caret + tab + text after caret
            this.value = val.substring(0, start) + "    " + val.substring(end);

            // put caret at right position again
            this.selectionStart = this.selectionEnd = start + 4;

            // prevent the focus lose
            return false;
        }
    });
});
