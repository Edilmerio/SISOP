$(document).ready(function() {
    App.init(); // initlayout and core plugins
    Base.init();
    TableGeneral.init();
    ListadoPagos.init();
});

var ListadoPagos = function () {
    var $a_nuevo_pago;

     var handler_event = function () {
        $a_nuevo_pago.on('click', function (event) {
            event.preventDefault();
            ModalGeneralOperacionesPago.load_nuevo_pago($(this).attr('href'));
        });
     };

    var inicializar_variables = function () {
         $a_nuevo_pago = $('#a_nuevo_pago');

    };

    return{
        init: function () {
            Base.activar_enlace($('#app_espectro_re'), $('#app_espectro_re_pagos'));
            inicializar_variables();
            handler_event();
        }
    }
}();