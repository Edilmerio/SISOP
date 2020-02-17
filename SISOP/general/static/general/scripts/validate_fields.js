let ValidateFields = function () {

    //funcion para validar un campo requerido
    //$elem -> elmento a validar requerido
    //$elem_notify -> elemento despues del cual se pondra la notify
    // message -> menaje a montrar
    // return false si no es valido
    let required = function ($elem, $elem_notify, message) {
        if ($elem.val().trim() === ""){
            add_messaje_error($elem_notify, message);
            return false;
        }
        else{
            delete_message_error($elem_notify, message);
        }
        return true;
    };

    //funcion que valida el valor de un campo
    //que debe ser mayor que value
    // return false si no es valido
    // value -> valor con que comparar
    let gt = function($elem, $elem_notify, value, message){
        let val_num = Number($elem.val());
        if (Number.isNaN(val_num)){
            add_messaje_error($elem_notify, 'Debe ser un #');
            return false;
        }
        else {
            delete_message_error($elem_notify, 'Debe ser un #');
            if (val_num <= value){
                add_messaje_error($elem_notify, message);
                return false;
            }
            else {
                delete_message_error($elem_notify, message);
            }
        }
        return true
    };

    // adiciona el mesaje de error despues de $e
    //$e elemto despues del cual se pone la notify
    // message mensaje a mostrar
    let add_messaje_error = function ($e, message) {
        let ul = $e.siblings('ul.errorlist');
        if (ul.length > 0){
            let add = true;
            ul.children('li').each(function () {
                if ($(this).text() === message){
                    add = false;
                }
            });
            if (add){
                ul.append(`<li>${message}</li>`);
            }
        }

        else{
            $e.after(`<ul class="errorlist"><li>${message}</li></ul>`);
        }
    };

    let delete_message_error = function ($e, message) {
        let ul = $e.siblings('ul.errorlist');
        ul.children('li').each(function () {
            if ($(this).text() === message){
                $(this).remove();
            }
        })
    };

    return{
        required: required,
        gt: gt
    }

}();