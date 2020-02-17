/**
 * Created by edilmerio.martinez on 15/06/2017.
 */


var Base = function(){

    var handle_events = function (){
         $('#modal_general').on('hidden.bs.modal', eliminar_elem_modal_general);
    };


    //elimina todos los elementos del cuerpo del modal
    var eliminar_elem_modal_general = function () {
        $('#div_modal_general_body').children().remove();
    };

    // Personalizacion para los canderarios
    var personalizacion_general= function () {
        $('.input-group.date').datepicker({
		    format: "dd/mm/yyyy",
		    language: "es",
		    autoclose: true,
		    showOnFocus: false,
		    allowInputToggle: true,
		//  todayBtn: 'linked',
		    todayHighlight: true,
            clearBtn: true
		});
    };

    // busca en el input id_input_notify si tine el formato type/title/text lanza la notificacion
    var notificacion_general = function () {
        notificacion($('#id_input_notify').val());
    };

    // funcion para invocar una notificacion con el formato recibe una cadena
    var notificacion = function (cadena) {
        if (cadena !== '') {
          var array_v = cadena.split('/');
            if (array_v.length !== 3 ||  !(array_v[0] === "success" || array_v[0] === "error" || array_v[0] === "info"))
                return;
            PNotify.alert({
                title: array_v[1],
                text: array_v[2],
                type: array_v[0],
                delay: 3000,
                styling: 'bootstrap3',
                icons: 'bootstrap3',
                addClass: 'pnotify_custom'
            });
        }
    };

    // funcion que activa el enlace de la barra izquierda y abre el acordion
    var activar_enlace = function ($elem_principal, $elem_secundario) {
       $elem_principal.children('a').click();
       $elem_principal.addClass('active');
       $elem_principal.children().children('span.marcar').addClass('selected');
       $elem_secundario.addClass('active');
    };

    var desactivar_link = function () {
      $('a[disabled]').attr('href','#');
    };

    return{
        init:function () {
            personalizacion_general();
            notificacion_general();
            handle_events();
            desactivar_link();
            // inicializar_variables();
        },
        personalizacion_general: personalizacion_general,
        notificacion: notificacion,
        activar_enlace: activar_enlace,
        $modal_cargando: $("#modal_cargando"),
        $modal_general: $('#modal_general'),
        $div_modal_general_body: $('#div_modal_general_body'),
        $modal_general_btn_guardar: $('#modal_general_btn_guardar')
    }

}();

base_js_operaciones_basicas={
  //  desabilita los emlementos recibidos anadiendo class desabiliado y attr disabled siempre que no tenga el attr disabled-server.
  desabilitar_elementos: function (elementos_add_class_desabilitado,elemento_add_attr_disabled) {
        $.each(elementos_add_class_desabilitado,function (index, elem) {
            $('#'+elem).addClass('desabilitado');
        });
        $.each(elemento_add_attr_disabled,function (index, elem) {
            if (!$('#'+elem).prop('disabled-server'))
                $('#'+elem).prop('disabled', true);
        });
    },
    // habilita los emlementos recibidos removiendo class desabiliado y attr disabled siempre que no tenga el attr disabled-server.
    habilitar_elementos: function (elementos_remove_class_desabilitado,elemento_remove_attr_disabled) {
        $.each(elementos_remove_class_desabilitado,function (index, elem) {
            $('#'+elem).removeClass('desabilitado');
        });
        $.each(elemento_remove_attr_disabled,function (index, elem) {
             // if (!$('#'+elem).prop('disabled-server'))
            $('#'+elem).removeProp('disabled', true);
        });
    },
    establecer_dia_inicial_and_final_datepickers: function (calendar, dia_inicial, dia_final) {
        $('#'+calendar).datepicker('setStartDate',dia_inicial);
        $('#'+calendar).datepicker('setEndDate',dia_final);
     }
};


