TableGeneral = function () {

    var handle_event = function () {
         $('#select_municipios').on('loaded.bs.select', add_btn_lista_municipios);
         $('table.table thead th a').on('click', enviar_server);
         $('ul.pagination a').on('click', enviar_server);
         $('#a_search').on('click', enviar_server);
         $('#input_search').on('keyup', observar_cambios_input_search);
         $('#a_exportar').on('click', enviar_server);
         $('#select_per_page').on('changed.bs.select', enviar_server)
     };

    var indicador_ordenable_table = function () {
        var a_ordenados_asc = $('table.table thead th.asc a');
        var a_ordenados_desc = $('table.table thead th.desc a');
        if(a_ordenados_asc.length > 0 ){
          $.each(a_ordenados_asc, function () {
              if ($(this).attr('href').search('sort=-id')!==-1 || $(this).attr('href').search('sort=id')!==-1||
                    $(this).attr('href').search('sort=-sistema')!==-1 || $(this).attr('href').search('sort=sistema')!==-1 )
              {
                  $(this).after('<i class="fa fa-sort-numeric-asc indicador-ordenar"></i>')
              }
              else
                   $(this).after('<i class="fa fa-sort-alpha-asc indicador-ordenar"></i>');
          })

        }
        if(a_ordenados_desc.length > 0){
           $.each(a_ordenados_desc, function () {
               if ($(this).attr('href').search('sort=-id')!==-1 || $(this).attr('href').search('sort=id')!==-1 ||
                    $(this).attr('href').search('sort=-sistema')!==-1 || $(this).attr('href').search('sort=sistema')!==-1)
               {
                    $(this).after('<i class="fa fa-sort-numeric-desc indicador-ordenar"></i>');
               }
                else
                    $(this).after('<i class="fa fa-sort-alpha-desc indicador-ordenar"></i>');
          })
        }
    };

    var add_btn_lista_municipios = function(){
        //
        $('#div_municipios ul').append('<li id="li_a_aceptar"><a id="a_aceptar_list_mun" class="btn btn-default" href="#">Aceptar</a></li>');
        $('#a_aceptar_list_mun').on('click', enviar_server);
    };

    var enviar_server = function () {
        var value_a_search = $('#input_search').val();
        var value_a_aceptar_list_mun = $('#div_municipios button[data-id="select_municipios"]').attr('title');
        var param_select_per_page = typeof ($('#select_per_page').val()) === 'undefined' ? 'per_pag=8' : 'per_pag='+$('#select_per_page').val();
        var $this = $(this);

        // cuando se presiona el enlace de la lista de los municipios
        if ($this.attr('id') === 'a_aceptar_list_mun'){
            window.location.href = '?search='+value_a_search+'&list_mun='+value_a_aceptar_list_mun + '&' + param_select_per_page;
        }
        // cuando se presiona el enlace de la busqueda
        else if ($this.attr('id') === 'a_search'){
            $this.attr('href','?search='+value_a_search+'&list_mun='+value_a_aceptar_list_mun + '&' + param_select_per_page);
        }
        // cuando se presiona los enlace de los campos de la tabla
        else if ($this.parent().hasClass('orderable')){
            $this.attr('href', '?sort='+ aux_buscar_href($this.attr('href'), 'sort=')
                +'&page=1&search='+value_a_search+'&list_mun='+value_a_aceptar_list_mun + '&' + param_select_per_page);
        }
        // cuando se presiona el enlace del paginador de la tabla
        else if ($this.parent().hasClass('next') || $this.parent().hasClass('previous')){
            $this.attr('href', '?sort='+ aux_buscar_href($this.attr('href'), 'sort=')
                +'&page='+aux_buscar_href($this.attr('href'), 'page=')+'&search='+value_a_search +
                '&list_mun='+value_a_aceptar_list_mun + '&' +param_select_per_page);
        }

        else if ($this.attr('id') === 'select_per_page'){
            var url = window.location.href;
            var url_mod_per_page = replace_value_parameter(url, 'per_pag', $this[0].value);

            window.location.href = replace_value_parameter(url_mod_per_page, 'page', 1);
        }

        // cuando se presiona el enlace exportar de la tabla.
        else if ($this.attr('id') === 'a_exportar'){
            var url = window.location.href;
            if (url.indexOf('?') === -1){
                url = url + '?_export=xlsx';
            }
            else{
                url = url + '&_export=xlsx';
            }
            $this.attr('href', url);
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

    var replace_value_parameter = function (url, param, value) {
    //    dada una url, parameter an and value, repalce that value or add parameter with value
          var index_busc = url.search(param);
          if (index_busc === -1){
              if (url.indexOf('?') === -1){
                  return (url + '?' +param + '=' + value);
              }
              else {
                  return (url + '&' + param + '=' + value);
              }
          }
          else {
              var value_param = aux_buscar_href(url, param);
              return url.replace(param + value_param, param + '=' + value);
          }
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

    var download_file = function (event) {
        // event.preventDefault();
        var queryString = window.location.search;
        var ind = window.location.pathname.slice(-1, window.location.pathname.length);
        var url =  $(this).attr('href').slice(0, $(this).attr('href').length-1) + ind + queryString;
        // $.fileDownload(url)
        //     .done(function () {
        //         alert('ok');
        //     })
        //     .fail(function () {
        //         alert('Ha ocurrido un error...');
        //     })
        // return false; //this is critical to stop the click event which will trigger a normal file download
        $(this).attr('href', url);
    };

    return{
        init: function () {
            indicador_ordenable_table();
            handle_event();
            establecer_focus_input_search();
        }
    }

}();