(function($) {
    $(document).ready(function() {
        $('form').submit(function() {
            if($("input[name=_save]").val() == "Выложить") {
                var confirmation = confirm("Выложить пост?");
                return confirmation;
            } else {
                return true;
            }
        });

        if($("input[name=_save]").length) {
            setInterval(function () {
                var postpone = $("input#id_postpone").prop("checked");

                var postponeTime = $(".form-row.field-postpone_time");
                var
                    saveButton = $("input[name=_save]"),
                    saveAndAddAnotherButton = $("input[name=_addanother]");

                if(postpone) {
                    postponeTime.show();
                    saveButton.val("Отложить");
                    saveAndAddAnotherButton.val("Отложить и создать другой пост");
                } else {
                    postponeTime.hide();
                    saveButton.val("Выложить");
                    saveAndAddAnotherButton.val("Выложить и создать другой пост");
                }
            }, 10);
        } else {
            var postpone = $(".form-row.field-postpone img").prop("alt") == "True";

            var postponeTime = $(".form-row.field-postpone_time");

            if(!postpone) {
                postponeTime.hide();
            }
        }
    });
})(django.jQuery);
