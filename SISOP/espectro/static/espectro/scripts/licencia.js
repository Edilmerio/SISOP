var Licencia = function () {

    var handle_events = function () {
        calendar_fecha_emision.datepicker().on('changeDate', logica_change_date_calendar_fecha_emision);
    };

    var calendar_fecha_emision;
    var calendar_fecha_vencimiento;

    var inicializar_variables = function () {
         calendar_fecha_emision = $('#calendar_fecha_emision');
         calendar_fecha_vencimiento = $('#calendar_fecha_vencimiento');
    };

    var estado_inicial_calendar_fecha_emision = function (fecha_autorizacion, fecha_autorizacion_start) {
        var fecha_ultima_lic = new Date($('#id_fecha_ultima_lic').val());
        var x = fecha_autorizacion !== null ? fecha_autorizacion : fecha_autorizacion_start;
        var min_fecha_emision = x > fecha_ultima_lic ? x : fecha_ultima_lic;
        var string_f_start = min_fecha_emision.getUTCDate() + '/' + ((min_fecha_emision.getUTCMonth() + 1).toString()) + '/' + min_fecha_emision.getUTCFullYear();
        base_js_operaciones_basicas.establecer_dia_inicial_and_final_datepickers('calendar_fecha_emision', string_f_start, '0d');
        var fecha_emision = calendar_fecha_emision.datepicker('getDate');
        if (fecha_emision < min_fecha_emision || fecha_autorizacion === null) {
            calendar_fecha_emision.datepicker('clearDates');
        }
        logica_change_date_calendar_fecha_emision();
    };

    var logica_change_date_calendar_fecha_emision = function () {
      var fecha_emision = calendar_fecha_emision.datepicker('getDate');
      var fecha_vencimiento = calendar_fecha_vencimiento.datepicker('getDate');
      if (fecha_vencimiento < fecha_emision || fecha_emision === null)
          calendar_fecha_vencimiento.datepicker('clearDates');
      var f_start = (fecha_emision !== null) ? fecha_emision : calendar_fecha_emision.datepicker('getStartDate');
      var string_f_start = f_start.getUTCDate() + '/' + (parseInt(f_start.getUTCMonth()) + 1).toString() + '/' + f_start.getUTCFullYear();
      base_js_operaciones_basicas.establecer_dia_inicial_and_final_datepickers('calendar_fecha_vencimiento', string_f_start, null);
    };

    return{
      init: function () {
          inicializar_variables();
          handle_events();
      },
      estado_inicial_calendar_fecha_emision: estado_inicial_calendar_fecha_emision
    };
}();