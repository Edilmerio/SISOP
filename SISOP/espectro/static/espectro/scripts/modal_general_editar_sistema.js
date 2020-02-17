var ModalGeneralEditarSistema = function () {

    var handle_event = function () {
        // $('#modal_general').on('shown.bs.modal', inicializar_modal_general);
    };

    var inicializar_modal_general = function(callback){
         var form_body_modal_general = $('#div_modal_general_body form');
         if (form_body_modal_general.length ===1){
             adicionar_form_button(form_body_modal_general);
             Base.personalizacion_general();
             App.initUniform();
             configurar_input_archivo_licencia();
             form_body_modal_general.submit(guardar_solicitud_licencia);
             var form_id = form_body_modal_general.attr('id');
             Licencia.init();
             if (form_id === 'form_editar_solicitud' || form_id === 'form_nueva_solicitud' ){
                 Solicitud.init();
                 configurar_input_archivo_solicitud();
             }
             if(form_id === 'form_nueva_licencia'){
                 Licencia.estado_inicial_calendar_fecha_emision(new Date('0001-01-01'), new Date('0001-01-01'));
             }

         }
          if (callback) callback();
    };

    // funcion que adiciona el atributo form a los botones correspondintes para provocar submit
    var adicionar_form_button = function (form) {
      $('#modal_general_btn_guardar').attr('form',form.attr('id'));
    };

     // funcion que raliza una llamada ajax pra guardar solicitud o licencia
    var guardar_solicitud_licencia = function (event) {
        event.preventDefault();
        var id_form = $(this).attr('id');
        habilitar_elem_modal_general();
        var data_form = new FormData($(this)[0]);
        $.ajax({
            // data: $(this).serialize(), // get the form data
            data: data_form,
            type: $(this).attr('method'), // GET or POST
            url: $(this).attr('action'), // the url to call
            dataType : 'html',
            processData: false,
            contentType: false,
            cache: false,
            success: function(response, status, jqXHR) { // on success..
                if (jqXHR.status === 209)
                    window.location.href = response;
                $('#id_input_notify_1').remove();  // elimina todos los input de notificaciones.
                var response_1 = $('<html />').html(response);   // crea un elemento para poder envolver la respuesta y poder aplicar
                var form_resp = response_1.find('form');
                if (form_resp.length === 1){
                    // es porque hay algun error en el llenado del formulario y se carga en el modal par la correccion.
                    $('#div_modal_general_body').html(response);
                    inicializar_modal_general();
                }
                else{
                    // es porque se guardo el formulario correctamente y se regargara la parte de la pagina
                    // correspondiente.
                    if (id_form === 'form_nueva_solicitud' || id_form ==='form_editar_solicitud'){
                        $('#div_sol_lic').remove();
                        $('#div_sol_lic_parent').html(response);

                    }
                    else if (id_form === 'form_nueva_licencia'){
                        $('#div_lic').html(response);
                    }
                    $('#modal_general').modal('hide');
                }
                Base.notificacion($('#id_input_notify_1').val());
                EditarSistema.handle_events();
            },
            error: function(jqXHR, status) {
                $('#modal_general').modal('hide');
                alert('Ha ocurrido un problema con el servidor...'+ status);
            }
        });
    };

    var habilitar_elem_modal_general = function () {
        $('#modal_general input[disabled]').prop('disabled',false);
        $('#modal_general select[disabled]').prop('disabled',false);
    };

    var configurar_input_archivo_solicitud = function () {
        var a_archivo_solicitud = $('#div_archivo_solicitud > a');
            if (a_archivo_solicitud.length === 1){
                a_archivo_solicitud.attr('href', '/espectro/descargar_fichero?dir='+
                                            a_archivo_solicitud.attr('href'));
                var cad = a_archivo_solicitud.text();
                a_archivo_solicitud.text(cad.substring(cad.lastIndexOf('/')+1));
                $(a_archivo_solicitud).after($('<button/>', {html : 'eliminar',
                            'class' : 'btn btn-primary btn-xs',
                            'id':'id_btn_eliminar_archivo_solicitud',
                            'type':'button',
                            'style':'margin-left:5px'
                        }));
                 $('#div_archivo_solicitud >label').hide();
                 $('#uniform-archivo_solicitud-clear_id').hide();

                $('#id_btn_eliminar_archivo_solicitud').click(function () {
                    $('#uniform-archivo_solicitud-clear_id > span').addClass('checked');
                    $('#archivo_solicitud-clear_id').prop('checked', true);
                    a_archivo_solicitud.hide();
                    $(this).hide();
                    $('#id_archivo_solicitud').prop('disabled',true);
                });
            }
    };

    var configurar_input_archivo_licencia = function () {
        var a_archivo_licencia = $('#div_archivo_licencia > a');
        if (a_archivo_licencia.length === 1){
            a_archivo_licencia.attr('href', '/espectro/descargar_fichero?dir='+
                a_archivo_licencia.attr('href'));
            var cad = a_archivo_licencia.text();
            a_archivo_licencia.text(cad.substring(cad.lastIndexOf('/')+1));
            $(a_archivo_licencia).after($('<button/>', {html : 'eliminar',
                'class' : 'btn btn-primary btn-xs',
                'id':'id_btn_eliminar_archivo_licencia',
                'type':'button',
                'style':'margin-left:5px'
            }));
            $('#div_archivo_licencia >label').hide();
            $('#uniform-archivo_licencia-clear_id > span').hide();

            $('#id_btn_eliminar_archivo_licencia').click(function () {
                $('#uniform-archivo_licencia-clear_id > span').addClass('checked');
                $('#archivo_licencia-clear_id').prop('checked', true);
                a_archivo_licencia.hide();
                $(this).hide();
                $('#id_archivo_licencia').prop('disabled',true);
            });
        }
    };
    
    return{
        init:function(){
          // handle_event();
        },
        inicializar_modal_general: inicializar_modal_general
    }

}();