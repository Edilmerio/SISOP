$(document).ready(function() {
    App.init(); // initlayout and core plugins
    Base.init();
    Sistema.init();
    EditarSistema.init();
    ModalGeneralEditarSistema.init();
});

 var EditarSistema = function () {

    var handle_events = function (){
        // desenlaza todos los controladores de enventos primero para evitar duplicidad de llamadas.
        $('#a_nueva_solicitud').unbind('click').click(form_solicitud_licencia);
        $('#id_btn_aceptar_sistema_and_radios').unbind('click').click(actualizar_valor_input);
        $('#div_sol ul.pagination a').unbind('click').click(listado_solicitudes_licencias);
        $('#div_lic ul.pagination a').unbind('click').click(listado_licencias);
        $('#div_sol td.licencia a').unbind('click').click(listados_licencias_sol_marcada);
        $('#div_sol td.editar a').unbind('click').click(form_solicitud_licencia);
        $('#a_nueva_lic').unbind('click').click(form_solicitud_licencia);

    };

    // funcion que realiza la llamada ajax para cagar los fornularios de nueva licencia, solcitud y editar solicitud
    var form_solicitud_licencia = function (event) {
        event.preventDefault();
        var url;
        if ($(this).attr('id') === 'a_nueva_lic'){
            var solicitud_id = $('#div_sol table tr.row-marcada td.id').text();
            url = '/espectro/nueva_licencia/'+solicitud_id;
        }
        else{
            url = $(this).attr('href');
        }
        Base.$modal_cargando.modal('show');
         $.ajax({
             type: 'GET',
             url: url,
             dataType : 'html',
             processData: false,
             contentType: false,
             cache: false,
             success: function(response, status, jqXHR) {
                 if (jqXHR.status === 209)
                     window.location.href = response;
                 $('#div_modal_general_body').html(response);
                 ModalGeneralEditarSistema.inicializar_modal_general(function () {
                     $('#modal_general').modal('show');
                 });
             },
             complete: function () {
                 Base.$modal_cargando.modal('hide');
             }

         });
         // configuracion inicial para el caso del link editar solicitud
        var ancho_modal='900px';
        var titulo_modal = 'Editar Solicitud';

        if ($(this).attr('id') === 'a_nueva_lic'){
            titulo_modal = 'Nueva Licencia';
            ancho_modal = '600px';
        }
        if ($(this).attr('id') === 'a_nueva_solicitud'){
            titulo_modal = 'Nueva Solicitud';
        }

        $('#modal_general div.modal-header h4').text(titulo_modal);
        $('#modal_general div.modal-dialog').width(ancho_modal);

    };

    // funcio para actualizar los input que tienen el numero de la pagina actual de la lista de las solicitudes y de las
    // licencias ademas de la solicitud marcada.
    var actualizar_valor_input= function () {
	    // para la obtener la pagina actual de la tb solicitud
        var pag_sol = 1;
        var pag_lic = 1;
        var id_row_marcada = -1;
        var li_pag_sol = $('#div_sol li.cardinality');
        if (li_pag_sol.length !== 0){
            var a = li_pag_sol.text();
            pag_sol = a.substring(a.search('Página ')+8, a.search(' de')-1);
            // para obtener el id de la row marcada
            var r = $('#div_sol table tr.row-marcada td.id');
            if (r.length !==0)
                id_row_marcada = r.text();
            // para la obtener la pagina actual de la tb licencias
            var li_pag_lic = $('#div_lic li.cardinality');
            if (li_pag_lic.length !== 0){
                var aa = li_pag_lic.text();
                pag_lic = aa.substring(aa.search('Página ')+8, aa.search(' de')-1);
            }

        }
        $('#ip_sol_page').val(pag_sol);
        $('#ip_lic_page').val(pag_lic);
        $('#ip_id_row_marcada').val(id_row_marcada);
    };

    // llamadas ajax para cargar solicitudes y licenicas cuando se pagina por el user las solicitudes
    var listado_solicitudes_licencias = function (event) {
	    event.preventDefault();
	    $("#modal_cargando").modal("show");
	    var url_original = $(location).attr('href');
	    var ind = url_original.search('"?"');
	    var id_sistema = -1;
	    if (ind === -1)
	        id_sistema = url_original.substring(url_original.lastIndexOf('/')+1);
        else
            id_sistema = url_original.substring(url_original.lastIndexOf('/')+1, ind-1);
        var url = '/espectro/listado_solicitudes_licencias/'+id_sistema.toString()+$(this).attr('href');
        cargar_llamada_ajax_load($('#div_sol_lic'), url);
    };

    // llamadas ajax para cargar licencias cuando el usuario pagina por las licencias
    var listado_licencias = function (event) {
        event.preventDefault();
	    var r = $('#div_sol table tr.row-marcada td.id');
	    if (r.length !==0)
	       var id_row_marcada = r.text();
	    else
	        id_row_marcada = '-1';
        var url ='/espectro/listado_licencias/'+id_row_marcada+$(this).attr('href');
        cargar_llamada_ajax_load($('#div_lic'), url);
    };

    // funcion que realiza una llamada ajax para cargar las licencias correspondientes a la solicitud marcada por el
    // usuario cuando este linkea licencias en la tabla solicitudes.
    var listados_licencias_sol_marcada = function (event) {
        event.preventDefault();
        $('#div_sol table tr.row-marcada').removeClass('row-marcada');
        $(this).parent().parent().addClass('row-marcada');
        cargar_llamada_ajax_load($('#div_lic'), $(this).attr('href'));
    };

    // funcion auxiliar para hacer una llamada ajax.load dado un contenedor y una url retorna true si no hay error.
    var cargar_llamada_ajax_load = function (contenedor, url, callback) {
        $("#modal_cargando").modal("show");
        contenedor.load( url, function( response, status, jqXHR){
            if (status === "error")
                $(location).attr('href','/general/NotFound');
            if (jqXHR.status === 209)
                window.location.href = response;
            if (jqXHR.status === 200){
                if (callback) callback();
                EditarSistema.handle_events();
            }
             $("#modal_cargando").modal("hide");
        });
    };

    return{
        init : function () {
            handle_events();
            Base.activar_enlace($('#app_espectro_re'), $('#app_espectro_re_nuevo_editar_sistema'));
        },
        handle_events: handle_events
    }
}();