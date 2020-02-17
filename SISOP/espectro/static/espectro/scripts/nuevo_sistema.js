$(document).ready(function() {
    App.init(); // initlayout and core plugins
    Base.init();
    Sistema.init();
    Licencia.init();
    Solicitud.init();
    NuevoSistema.init()
});

var NuevoSistema = function () {

    return{
        init: function () {
            Base.activar_enlace($('#app_espectro_re'), $('#app_espectro_re_nuevo_sistema'));
        }
    }

}();