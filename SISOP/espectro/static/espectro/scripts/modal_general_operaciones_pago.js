let ModalGeneralOperacionesPago = function () {

    let $btn_adicionar_sistema;
    let $form_operaciones_pago;

    let init1 = function () {
        handle_events();
        adicionar_form_button($form_operaciones_pago);
    };

    let load_nuevo_pago = function (url) {
        Base.$modal_cargando.modal("show");
        load_form(url, function () {
             Base.$modal_cargando.modal("hide");
             Base.$modal_general.modal('show');
             $('#modal_general div.modal-header h4').text('Nuevo Pago');
             $('#modal_general div.modal-dialog').width('1250px');
             Base.personalizacion_general();
             App.initUniform();
             inicializar_variables();
             init1();
             FormsetDjango.init();
             Pago.init();
        });
    };

    let load_form = function (url, callback) {
        Base.$div_modal_general_body.load( url, function( response, status, jqXHR){
            if (status === "error")
                $(location).attr('href','/general/NotFound');
            if (jqXHR.status === 209)
                window.location.href = response;
            if (jqXHR.status === 200){
                if (callback) callback();
            }

        });
    };

    let inicializar_variables = function () {
       $btn_adicionar_sistema = $('#btn_adicionar_sistema');
       $form_operaciones_pago = $('#modal_operaciones_pago');
    };

    let handle_events = function () {
        $btn_adicionar_sistema.on('click', add_form_to_formset);
        $form_operaciones_pago.on('submit', save_pago);
        $('.delete-form').on('click', delete_form_to_formset);
        $('.sistema').on('blur', Pago.check_sistema);
    };

    let add_form_to_formset = function (event) {
        event.preventDefault();
        FormsetDjango.add_form_to_formset($('#div_form-0'), $('#div_aux'), $('#div_sistemas'),function () {
           $('.form-dinamico .delete-form').attr('disabled', false);
           $('.delete-form').on('click', delete_form_to_formset);
           $('.sistema').off('blur', Pago.check_sistema);
           $('.sistema').on('blur', Pago.check_sistema);
           Pago.init_typeahead();
           Base.personalizacion_general();
        });
    };

    let delete_form_to_formset = function () {
      FormsetDjango.delete_form_to_formset($(this).parents('.form-dinamico').get(0));
    };

    let adicionar_form_button = function (form) {
      Base.$modal_general_btn_guardar.attr('form',form.attr('id'));
    };

    let save_pago = function(ev){
        ev.preventDefault();
        if (true){
            Base.$modal_cargando.modal('show');
            let form = $('#modal_operaciones_pago');
            let data_form = new FormData(form[0]);
            $.ajax({
                // data: $(this).serialize(), // get the form data
                data: data_form,
                type: form.attr('method'), // GET or POST
                url: form.attr('action'), // the url to call
                dataType: 'html',
                processData: false,
                contentType: false,
                cache: false,
                success: function (response, status, jqXHR) { // on success..
                    if (jqXHR.status === 209){
                        window.location.href = response;
                    }
                    $('#id_input_notify_1').remove();  // elimina todos los input de notificaciones.
                    let response_1 = $('<html />').html(response);   // crea un elemento para poder envolver la respuesta y poder aplicar
                    let form_resp = response_1.find('form');
                    if (form_resp.length === 1) {
                        // es porque hay algun error en el llenado del formulario y se carga en el modal par la correccion.
                        Base.$div_modal_general_body.html(response);
                    }
                    Base.personalizacion_general();
                    App.initUniform();
                    inicializar_variables();
                    init1();
                    FormsetDjango.init();
                    Pago.init();
                    Base.notificacion($('#id_input_notify_1').val());
                },
                error: function (jqXHR, status) {
                    Base.$modal_cargando.modal("hide");
                    alert('Ha ocurrido un problema con el servidor...' + status);
                },
                complete: function () {
                    Base.$modal_cargando.modal("hide");
                }
            });
        }
        else {
         Base.notificacion('error/ERROR/Corrija los errores... Pruebe otra vez...')
        }

    };

    let save_subcripcion = function (event) {
        event.preventDefault();
        save_form_subcripcion($form_subcripcion);

    };

    let save_form_subcripcion = function (form) {
        Base.$modal_cargando.modal('show');
        let data_form = new FormData(form[0]);
        $.ajax({
            // data: $(this).serialize(), // get the form data
            data: data_form,
            type: form.attr('method'), // GET or POST
            url: form.attr('action'), // the url to call
            dataType: 'html',
            processData: false,
            contentType: false,
            cache: false,
            success: function (response, status, jqXHR) { // on success..
                if (jqXHR.status === 209)
                    window.location.href = response;
                $input_notify_1.remove();  // elimina todos los input de notificaciones.
                let response_1 = $('<html />').html(response);   // crea un elemento para poder envolver la respuesta y poder aplicar
                let form_resp = response_1.find('form');
                if (form_resp.length === 1) {
                    // es porque hay algun error en el llenado del formulario y se carga en el modal par la correccion.
                    Base.$div_modal_general_body.html(response);
                }
                // init_subcripcion();
                 Base.personalizacion_general();
                 App.initUniform();
            },
            error: function (jqXHR, status) {
                alert('Ha ocurrido un problema con el servidor...' + status);
            }
        });
        Base.$modal_cargando.modal('hide');
        Base.$modal_general.modal('hide');
    };

    return{
       load_nuevo_pago: load_nuevo_pago
    };
}();