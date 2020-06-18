$(document).ready(function() {
    App.init(); // initlayout and core plugins
    Base.init();
    Indicadores.init();
});

let Indicadores = function () {

    let calendar_fecha_inicio;
    let calendar_fecha_fin;
    let is_cargar;
    let fecha_inicio_disponible;
    let fecha_fin_disponible;

    let handle_events = function (){
        calendar_fecha_inicio.datepicker().on('changeDate', change_datepicker_fecha_inicio);
        calendar_fecha_fin.datepicker().on('changeDate', change_datepicker_fecha_fin);
        $('#a_ind_diario').bind('click').click(toggle_indicadores_diario_acumulado);
        $('#a_ind_acumulado').bind('click').click(toggle_indicadores_diario_acumulado);
        $('#btn_aceptar').on('click', load_indicadores);
        $('#a_actualizar_lineas_servicio').on('click', load_lineas_servicio);
        $('#a_exportar').on('click', exportar_data);
    };

    let inicializar_variables = function(){
        calendar_fecha_inicio = $('#calendar_fecha_inicio');
        calendar_fecha_fin = $('#calendar_fecha_fin');
        is_cargar = true;
        let f1_aux_utc = new Date($('#id_fecha_inicio_disponible').val());
        fecha_inicio_disponible = new Date(new Date(f1_aux_utc).getTime() + f1_aux_utc.getTimezoneOffset()*60*1000);
        let f2_aux_utc = new Date($('#id_fecha_fin_disponible').val());
        fecha_fin_disponible = new Date(new Date(f2_aux_utc).getTime() + f2_aux_utc.getTimezoneOffset()*60*1000);
    };
    let init_datepicker = function(){
    //    estable las fehcas disponibles para los datapicker
        base_js_operaciones_basicas
            .establecer_dia_inicial_and_final_datepickers('calendar_fecha_inicio',
                fecha_inicio_disponible, fecha_fin_disponible);

    };

    let update_fecha_export = function(){
        let fecha_inicio_export = $('#fecha_inicio').val();
        let fecha_fin_export = fecha_inicio_export;
        if ($('#li_ind_acumulado').hasClass('active') === true){
            fecha_fin_export = $('#fecha_fin').val();
        }
        $('#id_fecha_inicio_export').val(fecha_inicio_export);
        $('#id_fecha_fin_export').val(fecha_fin_export);
    };

    let toggle_indicadores_diario_acumulado = function (event) {
        event.preventDefault();
        let $this = $(this);
        $this.parent().addClass('active');
        $this.parent().siblings().removeClass('active');
        logica_ind_diarios_acumulado_active();
    };
    let logica_ind_diarios_acumulado_active = function () {
        let ayer = new Date(Date.now()-86400000);
        let f_prop = fecha_fin_disponible >= ayer? ayer:fecha_fin_disponible;
        if ($('#li_ind_diario').hasClass('active') === true){
            $('#btn_aceptar').prop('disabled', false);
            $('#div_fecha_fin').hide('fast');
            if (is_cargar !== true){
                calendar_fecha_inicio.datepicker('setDate', f_prop);
            }
            else
                is_cargar = false;
        }
        if ($('#li_ind_acumulado').hasClass('active') === true){
            $('#div_fecha_fin').show('fast', function () {
                calendar_fecha_fin.datepicker('setDate', f_prop);
            });
            let firstDay = new Date(ayer.getFullYear(), ayer.getMonth(), 1);
            let f_prop1 = (firstDay >=fecha_inicio_disponible && firstDay <=fecha_fin_disponible)? firstDay: fecha_inicio_disponible;
            calendar_fecha_inicio.datepicker('setDate', f_prop1);
        }
    };

    let change_datepicker_fecha_inicio = function () {
        let f_start = calendar_fecha_inicio.datepicker('getDate');
        let f_fin_mes = new Date(f_start.getFullYear(), f_start.getMonth() + 1, 0);
        if ($('#li_ind_acumulado').hasClass('active') === true){
            let f_fin = calendar_fecha_fin.datepicker('getDate');
            if (f_start > f_fin || f_start === null || f_fin > f_fin_mes){
                calendar_fecha_fin.datepicker('clearDates');
                $('#btn_aceptar').prop('disabled', true);
            }
            else {
                $('#btn_aceptar').prop('disabled', false);
            }
            let f_fin_1 = f_fin_mes < fecha_fin_disponible? f_fin_mes:fecha_fin_disponible;
            base_js_operaciones_basicas
                .establecer_dia_inicial_and_final_datepickers('calendar_fecha_fin', f_start, f_fin_1);
        }
    };

    let change_datepicker_fecha_fin = function () {
        if (calendar_fecha_inicio.datepicker('getDate') === null)
            $('#btn_aceptar').prop('disabled', true);
        else {
            if ($('#li_ind_acumulado').hasClass('active') === true){
                $('#btn_aceptar').prop('disabled', false);
            }
        }

    };

    let load_indicadores = function () {
        let fecha_inicio = $('#fecha_inicio').val();
        let fecha_fin = fecha_inicio;
        if ($('#li_ind_acumulado').hasClass('active') === true){
            fecha_fin = $('#fecha_fin').val();
        }
        Base.$modal_cargando.modal('show');
        let url = '/parte_diario/table_indicadores?fecha_inicio=' + fecha_inicio + '&fecha_fin=' + fecha_fin;
        $.ajax({
            type: 'GET',
            url: url,
            dataType : 'html',
            processData: false,
            contentType: false,
            cache: false,
            success: function(response, status, jqXHR) {
                if (jqXHR.status === 209){
                    window.location.href = response;
                    return;
                }
                $('#div_tables_indicadores').html(response);
                update_fecha_export();
            },
            complete: function () {
                Base.$modal_cargando.modal('hide');
            },
            error: function(jqXHR, status) {
                alert('Ha ocurrido un problema con el servidor...'+ status);
            }

        });
    };

    let load_lineas_servicio = function (event) {
        event.preventDefault();
        let href = $(this).attr('href');
        if (href === '#'){
            return;
        }
        ModalGeneralLineasServicio.load_lineas_servicio($(this).attr('href'));
    };

    let exportar_data = function () {
        let url = '/parte_diario/table_indicadores?fecha_inicio='
            + $('#id_fecha_inicio_export').val() + '&fecha_fin=' + $('#id_fecha_fin_export').val() + '&_export=xlsx';
        $(this).attr('href', url)
    };

    let set_datepicker_inicio_aux = function () {
        $('#calendar_fecha_inicio').datepicker('setDate', $('#fecha_inicio').val())
    };

    return{
        init: function () {
            inicializar_variables();
            init_datepicker();
            handle_events();
            Base.activar_enlace($('#app_parte_diario'), $('#app_parte_diario_indicadores'));
            logica_ind_diarios_acumulado_active();
            update_fecha_export();
        },
        load_indicadores: load_indicadores,
        init_datepicker: init_datepicker,
        set_datepicker_inicio_aux: set_datepicker_inicio_aux
    }

}();