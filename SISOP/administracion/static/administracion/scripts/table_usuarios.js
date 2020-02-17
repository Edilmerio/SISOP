TableUsuarios = function () {

    var handle_event = function () {
         $('ul.pagination a').on('click', enviar_server);
         $('#a_search').on('click', enviar_server);
         $('#input_search').on('keyup', observar_cambios_input_search);
     };

    var enviar_server = function () {
        var value_a_search = $('#input_search').val();
        var $this = $(this);
        // cuando se presiona el enlace de la busqueda
        if ($this.attr('id') === 'a_search'){
            $this.attr('href','?search='+value_a_search);
        }
        // cuando se presiona el enlace del paginador de la tabla
        else if ($this.parent().hasClass('next') || $this.parent().hasClass('previous')){
            $this.attr('href', '?page='+aux_buscar_href($this.attr('href'), 'page=')+'&search='+value_a_search);
        }
    };

    var aux_buscar_href = function (cadena, param) {
             var index_busc = cadena.search(param);
              if (index_busc === -1)
                  return '';
             var resto = cadena.substring(index_busc + param.length);
             if (resto.search('&') === -1)
                return resto;
            return resto.substring(0, resto.indexOf('&'));
        };

    var observar_cambios_input_search = function (e) {
        var tecla = (document.all) ? e.keyCode : e.which;
        if (tecla === 13 ) {
           document.getElementById('a_search').click();
        }
    };
    var establecer_focus_input_search = function () {
        var input_search =  $('#input_search');
        input_search .focus();
        var temp =input_search .val();
        input_search .val('');
        input_search .val(temp);
    };

    return{
        init: function () {
            handle_event();
            establecer_focus_input_search();
        }
    }

}();