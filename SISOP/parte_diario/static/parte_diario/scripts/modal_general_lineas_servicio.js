let ModalGeneralLineasServicio = function () {

    let $form_actualizar_lineas_servicio;

    let init1 = function () {
        handle_events();
        adicionar_form_button($form_actualizar_lineas_servicio);
    };

    let load_lineas_servicio = function (url) {
        Base.$modal_cargando.modal("show");
        load_form(url, Base.$div_modal_general_body, function () {
            Base.$modal_cargando.modal("hide");
            Base.$modal_general.modal('show');
            $('#modal_general div.modal-header h4').text('Actualizar Líneas en Servicio');
            $('#modal_general div.modal-dialog').width('800px');
            App.initUniform();
            inicializar_variables();
            init1();
        });
    };

    let load_form_lineas_servicio = function(){
        Base.$modal_cargando.modal("show");
        let url = '/parte_diario/form_lineas_servicio?fecha=' + $('#fecha_lineas').val();
        load_form(url, $('#div_form_lineas_servicio'),function () {
            Base.$modal_cargando.modal("hide");
            $form_actualizar_lineas_servicio = $('#form_actualizar_lineas_servicio');
            $form_actualizar_lineas_servicio.on('submit', save_actualizar_lineas);
        });
    };

    let load_form = function (url, $place_put_response, callback) {
        $place_put_response.load( url, function( response, status, jqXHR){
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
        $form_actualizar_lineas_servicio = $('#form_actualizar_lineas_servicio');
        $('.input-group.date').datepicker('remove');
        $("#calendar_fecha_lineas").datepicker( {
            format: "mm/yyyy",
            startView: "months",
            minViewMode: "months",
            autoclose: true,
        });
        let f1_aux_utc = new Date($('#id_last_day_month').val());
        let f_fin_mes = new Date(new Date(f1_aux_utc).getTime() + f1_aux_utc.getTimezoneOffset()*60*1000);
        base_js_operaciones_basicas
            .establecer_dia_inicial_and_final_datepickers('calendar_fecha_lineas', null, f_fin_mes);
    };

    let handle_events = function () {
        $form_actualizar_lineas_servicio.on('submit', save_actualizar_lineas);
        Base.$modal_general.on('hidden.bs.modal', restart_datepicker_indicadores);
        $('#calendar_fecha_lineas').datepicker().on('changeDate', load_form_lineas_servicio);
    };

    let adicionar_form_button = function (form) {
        Base.$modal_general_btn_guardar.attr('form',form.attr('id'));
    };

    let restart_datepicker_indicadores = function(){
        Base.personalizacion_general();
        Indicadores.init_datepicker();
        Indicadores.set_datepicker_inicio_aux();

    };

    let save_actualizar_lineas = function(ev){
        ev.preventDefault();
            Base.$modal_cargando.modal('show');
            let form = $form_actualizar_lineas_servicio;
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
                    $('#id_input_notify_1').remove();  // elimina todos los input de notificaciones.
                    let response_1 = $('<html />').html(response);   // crea un elemento para poder envolver la respuesta y poder aplicar
                    let form_resp = response_1.find('form');
                    if (form_resp.length === 1) {
                        // es porque hay algun error en el llenado del formulario y se carga en el modal par la correccion.
                        Base.$div_modal_general_body.html(response);
                        Base.personalizacion_general();
                        App.initUniform();
                        inicializar_variables();
                        init1();
                        Base.notificacion($('#id_input_notify_1').val());
                    }
                    else {
                        Indicadores.load_indicadores();
                        Base.$modal_general.modal('hide');
                        Base.notificacion(response);
                    }

                },
                error: function (jqXHR, status) {
                    Base.$modal_cargando.modal("hide");
                    alert('Ha ocurrido un problema con el servidor...' + status);
                },
                complete: function () {
                    Base.$modal_cargando.modal("hide");
                }
            });
    };
    return{
        load_lineas_servicio: load_lineas_servicio
    };
}();