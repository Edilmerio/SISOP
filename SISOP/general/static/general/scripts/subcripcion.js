var Subcripcion = function () {

    var $btn_guardar_subcripcion;
    var $a_subcripcion;
    var $modal_general;
    var $modal_cargando;
    var $form_subcripcion;
    var $div_modal_general_body;
    var $select_place_info;
    var $modal_general_btn_guardar;
    var $input_notify_1;


    var inicializar_variables_before = function () {
         $a_subcripcion = $('#a_subcripcion');
         $modal_cargando = $("#modal_cargando");
         $modal_general = $('#modal_general');
         $div_modal_general_body = $('#div_modal_general_body');
         $modal_general_btn_guardar = $('#modal_general_btn_guardar');
    };

    var handle_events_before = function () {
        $a_subcripcion.on('click', load_subcripcion);
    };

    var before_load = function () {
    //    antes que se cargue el form de la subcripcion
        inicializar_variables_before();
        handle_events_before();
    };

    var load_subcripcion = function (event) {
        event.preventDefault();
        var url = $a_subcripcion.attr('href');
        $modal_cargando.modal("show");
        load_form_subcripcion(url, function () {
             $modal_cargando.modal("hide");
             $modal_general.modal('show');
             $('#modal_general div.modal-header h4').text('Suscripción de información');
             $('#modal_general div.modal-dialog').width('500px');
             init_subcripcion();
        });
    };

    var load_form_subcripcion = function (url, callback) {
        $div_modal_general_body.load( url, function( response, status, jqXHR){
            if (status === "error")
                $(location).attr('href','/general/NotFound');
            if (jqXHR.status === 209)
                window.location.href = response;
            if (jqXHR.status === 200){
                if (callback) callback();
            }

        });
    };

    var init_subcripcion = function () {
        inicializar_variables();
        handle_events();
        adicionar_form_button($form_subcripcion);
        add_action_fom();
        $select_place_info.selectpicker('refresh');
    };

    var inicializar_variables = function () {
        $btn_guardar_subcripcion = $('#modal_general_btn_guardar');
        $form_subcripcion = $('#form_subcripcion');
        $select_place_info = $('#select_place_info');
        $input_notify_1 = $('#id_input_notify_1');
    };

    var handle_events = function () {
        $form_subcripcion.submit(save_subcripcion);
    };

    var adicionar_form_button = function (form) {
      $modal_general_btn_guardar.attr('form',form.attr('id'));
    };

    var add_action_fom = function () {
      $form_subcripcion.attr('action', $a_subcripcion.attr('href'));
    };

    var save_subcripcion = function (event) {
        event.preventDefault();
        save_form_subcripcion($form_subcripcion);

    };

    var save_form_subcripcion = function (form) {
        $modal_cargando.modal('show');
        var data_form = new FormData(form[0]);
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
                var response_1 = $('<html />').html(response);   // crea un elemento para poder envolver la respuesta y poder aplicar
                var form_resp = response_1.find('form');
                if (form_resp.length === 1) {
                    // es porque hay algun error en el llenado del formulario y se carga en el modal par la correccion.
                    $div_modal_general_body.html(response);
                }
                // init_subcripcion();
                Base.notificacion(response_1.find('#id_input_notify_1').val());
            },
            error: function (jqXHR, status) {
                alert('Ha ocurrido un problema con el servidor...' + status);
            }
        });
        $modal_cargando.modal('hide');
        $modal_general.modal('hide');
    };

    return{
       before_load: before_load
    };
}();