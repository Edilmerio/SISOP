var Solicitud = function () {

    var handle_events = function () {
        cbx_solicitud_enviada.click(logica_solicitud_licencia);
        cbx_solicitud_autorizada.click(logica_solicitud_licencia);
        calendar_fecha_envio.datepicker().on('changeDate', logica_change_date_calendar_fecha_envio);
        calendar_fecha_autorizacion.datepicker().on('changeDate', logica_change_date_calendar_fecha_autorizacion);
        select_tipo_solicitud.change(logica_change_tipo_solicitud);
    };

    var cbx_solicitud_enviada;
    var cbx_solicitud_autorizada;
    var calendar_fecha_envio;
    var calendar_fecha_autorizacion;
    var select_tipo_solicitud;

    var elementos_add_or_remove_class_desabilitado_solucitud= ['div_fecha_envio','div_archivo_solicitud',
            'div_cbx_solicitud_autorizada', 'div_tipo_solicitud'];
    var elementos_add_or_remove_class_desabilitado_licencia= ['div_fecha_autorizacion', 'div_licencia' ];
    var elementos_add_or_remove_attr_disabled_solicitud=['id_fecha_envio', 'id_archivo_solicitud',
            'cbx_solicitud_autorizada','id_tipo_solicitud'];
    var elementos_add_or_remove_attr_disabled_licencia=['id_fecha_autorizacion', 'id_fecha_emision',
            'id_fecha_vencimiento', 'id_archivo_licencia', 'id_licencia'];

    // Solo es necesario para asignacion de elementos cuando a la hora de cargar el js no estan aun.
    var inicializar_variables = function () {
        cbx_solicitud_enviada = $('#cbx_solicitud_enviada');
        cbx_solicitud_autorizada = $('#cbx_solicitud_autorizada');
        calendar_fecha_envio = $('#calendar_fecha_envio');
        calendar_fecha_autorizacion = $('#calendar_fecha_autorizacion');
        select_tipo_solicitud = $('#id_tipo_solicitud');
    };


    var logica_solicitud_licencia = function () {
        if (!cbx_solicitud_enviada.prop('disabled')){
            if (!cbx_solicitud_enviada.prop('checked')) {
             base_js_operaciones_basicas.desabilitar_elementos(
                elementos_add_or_remove_class_desabilitado_solucitud, elementos_add_or_remove_attr_disabled_solicitud);
             base_js_operaciones_basicas.desabilitar_elementos(elementos_add_or_remove_class_desabilitado_licencia,
                elementos_add_or_remove_attr_disabled_licencia)
            }
            else{
             base_js_operaciones_basicas.habilitar_elementos(elementos_add_or_remove_class_desabilitado_solucitud,
                elementos_add_or_remove_attr_disabled_solicitud);
            if( !cbx_solicitud_autorizada.prop('checked')){
                 base_js_operaciones_basicas.desabilitar_elementos( elementos_add_or_remove_class_desabilitado_licencia,
                        elementos_add_or_remove_attr_disabled_licencia);
            }
            else{
                 if ($('#id_tipo_solicitud option:selected').text() === 'BAJA') {
                     base_js_operaciones_basicas.desabilitar_elementos(elementos_add_or_remove_class_desabilitado_licencia,
                         elementos_add_or_remove_attr_disabled_licencia);
                     base_js_operaciones_basicas.habilitar_elementos(['div_fecha_autorizacion'], ['id_fecha_autorizacion']);
                 }
                 else
                     base_js_operaciones_basicas.habilitar_elementos(elementos_add_or_remove_class_desabilitado_licencia,
                       elementos_add_or_remove_attr_disabled_licencia);
                }
            }
        }
        else{
            if (!cbx_solicitud_autorizada.prop('disabled')){
                if( !cbx_solicitud_autorizada.prop('checked')){
                 base_js_operaciones_basicas.desabilitar_elementos( elementos_add_or_remove_class_desabilitado_licencia,
                   elementos_add_or_remove_attr_disabled_licencia);
            }
            else{
                 if ($('#id_tipo_solicitud option:selected').text() === 'BAJA') {
                     base_js_operaciones_basicas.desabilitar_elementos(elementos_add_or_remove_class_desabilitado_licencia,
                         elementos_add_or_remove_attr_disabled_licencia);
                     base_js_operaciones_basicas.habilitar_elementos(['div_fecha_autorizacion'], ['id_fecha_autorizacion']);
                 }
                 else
                     base_js_operaciones_basicas.habilitar_elementos(elementos_add_or_remove_class_desabilitado_licencia,
                       elementos_add_or_remove_attr_disabled_licencia);
                }
            }
        }
    };

    var estado_inicial_calendar_fecha_envio = function () {
         var fecha_ultima_sol = $('#id_fecha_ultima_sol').val();
         base_js_operaciones_basicas.establecer_dia_inicial_and_final_datepickers('calendar_fecha_envio', fecha_ultima_sol, '0d');
         logica_change_date_calendar_fecha_envio();
    };

    var logica_change_date_calendar_fecha_envio = function () {
        var fecha_envio = calendar_fecha_envio.datepicker('getDate');
        var start_day_calendar_fecha_envio = calendar_fecha_envio.datepicker('getStartDate');
        var f_start = fecha_envio !== null ? fecha_envio : start_day_calendar_fecha_envio;
        var string_f_start = f_start.getUTCDate()+'/'+(parseInt(f_start.getUTCMonth())+1).toString()+'/'+f_start.getUTCFullYear();
        base_js_operaciones_basicas.establecer_dia_inicial_and_final_datepickers('calendar_fecha_autorizacion', string_f_start, '0d');
        var fecha_autorizacion = calendar_fecha_autorizacion.datepicker('getDate');
        if(fecha_envio == null || fecha_autorizacion == null || fecha_autorizacion < f_start )
            if (!$('#id_fecha_envio').prop('disabled'))
                calendar_fecha_autorizacion.datepicker('clearDates');
        logica_change_date_calendar_fecha_autorizacion();
    };

    var logica_change_date_calendar_fecha_autorizacion = function () {
        Licencia.estado_inicial_calendar_fecha_emision(calendar_fecha_autorizacion.datepicker('getDate'), calendar_fecha_autorizacion.datepicker('getStartDate'));
    };

    var logica_change_tipo_solicitud = function(){
        if ($('#id_tipo_solicitud option:selected').text() === 'BAJA')
            $('#id_mensaje_alerta_solicitud_baja').show('slow');
        else
             $('#id_mensaje_alerta_solicitud_baja').hide('fast');
        logica_solicitud_licencia();
    };
    return{
        init: function () {
            inicializar_variables();
            handle_events();
            logica_solicitud_licencia();
            estado_inicial_calendar_fecha_envio();
            logica_change_tipo_solicitud();
      }
    };
}();