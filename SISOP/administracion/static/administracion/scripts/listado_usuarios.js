$(document).ready(function() {
    App.init(); // initlayout and core plugins
    Base.init();
    TableUsuarios.init();
    ListadoUsuarios.init()
});

var ListadoUsuarios = function () {
    var handle_events = function () {
        $('#div_encabezado_busqueda td.permisos a').click(form_permisos);

    };

    var form_permisos = function (event) {
        event.preventDefault();
        url = $(this).attr('href');
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'html',
            processData: false,
            contentType: false,
            cache: false,
            success: function (response, status, jqXHR) {
                if (jqXHR.status === 209)
                    window.location.href = response;
                $('#div_modal_general_body').html(response)
                $('select').selectpicker();
                $('#modal_general').modal('show');
                $('#div_modal_general_body form').submit(guardar_cambios_permisos);
                adicionar_form_button();
            },
            error: function (jqXHR, status) {
                alert('Ha ocurrido un problema con el servidor...' + status);
            }
        });
        $('#modal_general div.modal-header h4').text('Editar Permisos');
        $('#modal_general div.modal-dialog').width('400px');
    };

    var guardar_cambios_permisos = function (event) {
        event.preventDefault();
        var data_form = new FormData($(this)[0]);
        $('#modal_general').modal('hide');
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
                Base.notificacion(response);
            },
            error: function(jqXHR, status) {
                alert('Ha ocurrido un problema con el servidor...'+ status);
            }
        });
    };

    var adicionar_form_button = function () {
         var form = $('#div_modal_general_body form');
         if (form.length === 1)
             $('#modal_general_btn_guardar').attr('form',form.attr('id'));
    };
    return{
        init: function () {
            Base.activar_enlace($('#app_administracion'), $('#app_administracion_usuarios'));
            handle_events();
        }
    }

}();