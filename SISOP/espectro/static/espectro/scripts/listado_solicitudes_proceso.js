$(document).ready(function() {
    App.init(); // initlayout and core plugins
    Base.init();
    TableGeneral.init();
    ListadoSolicitudesProceso.init();
    Subcripcion.before_load();
});

var ListadoSolicitudesProceso = function () {

    return {
        init: function () {
            Base.activar_enlace($('#app_espectro_re'), $('#app_espectro_re_solicitudes'));
        }
    }

}();