    var Sistema = function () {

    var handle_event = function () {
      $('.add-form').click(adicionar_form);
      $('.delete-form').click(eliminar_form);
      $('#id_equipo').change(llenar_input_equipo);
      $('#id_tipo_sistema').change(lista_equipos);
    };

    // var div_form_dinamico = $('div.form-dinamico');

    var llenar_input_equipo = function () {
      var valor =$('#id_equipo option:selected').text();
      $('div.form-dinamico').each(function() {
          $(this).find('.inp_equipo').val(valor);
      });
    };

    var actualizar_attr_elem_forms =function(){
		var prefix='form';
		var id_regex = new RegExp('(' + prefix + '-\\d+)');
		// var form_count=$('.form-dinamico').length;
		$('div.form-dinamico').each(function(index){
			var replacement = prefix + '-' + index;
			if($(this).attr('id')) $(this).attr('id',$(this).attr('id').replace(id_regex, replacement));
			$(this).children().children().each(function(){
				if ($(this).attr('for')) $(this).attr('for', $(this).attr('for').replace(id_regex, replacement));
				if($(this).attr('id')) $(this).attr('id',$(this).attr('id').replace(id_regex, replacement));
				if($(this).attr('name')) $(this).attr('name',$(this).attr('name').replace(id_regex, replacement));
				});
			$(this).find(':input[type=checkbox]').each(function(){
				if ($(this).attr('for')) $(this).attr('for', $(this).attr('for').replace(id_regex, replacement));
				if($(this).attr('id')) $(this).attr('id',$(this).attr('id').replace(id_regex, replacement));
				if($(this).attr('name')) $(this).attr('name',$(this).attr('name').replace(id_regex, replacement));
			    });
			});
		};

    var adicionar_form = function () {
       var prefix='form';
         var form_count = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
         var form_parent=$(this).parents('.form-dinamico').get(0);
         var form_clone=$(form_parent).clone(true);
         $(form_clone).find('ul.errorlist').remove();
		 $(form_clone).find(':input[type=text]').val('');
		 $(form_clone).find('input[type=hidden]').remove();
		 $(form_parent).after(form_clone);
		 $('#id_' + prefix + '-TOTAL_FORMS').val(form_count + 1);
		// $('#id_' + prefix + '-INITIAL_FORMS').val(form_count + 1);
		 $('.form-dinamico .delete-form').attr('disabled', false);
       actualizar_attr_elem_forms();
       llenar_input_equipo();
    };

    var eliminar_form = function () {
        var prefix='form';
		//$(this).parents('.form-dinamico').get(0).remove();
        var form_parent = $(this).parents('.form-dinamico').get(0);
        if ($(form_parent).find('input[type=hidden]').length === 0 || $(form_parent).find('input[type=hidden]').val()==='' )
            form_parent.remove();
        else{
            $(form_parent).find('div.checker input[type=checkbox]').prop('checked', true);
            $(form_parent).find('div.checker span').addClass('checked');
            $(form_parent).css('display', 'none');
        }
        var forms = $('.form-dinamico');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        desabilitar_btn_eliminar();
        actualizar_attr_elem_forms();
    };
    //desabilita el boton eliminar radios cuando solo queda un radio
    var desabilitar_btn_eliminar = function () {
        var forms = $('.form-dinamico');
        if( forms.filter(':visible').length===1)
            $('.form-dinamico .delete-form').attr('disabled', true);
    };

    var lista_equipos = function () {
        $("#modal_cargando").modal("show");
		var request=$.ajax({
			url: '/espectro/lista_equipos/'+$(this).val(),
			dataType: 'json'
        });
		request.done(function(data_json){
			var option_equipos='';
			$.each(data_json,function(i,item){
				option_equipos+='<option value="'+item['pk'].toString()+'">'+item['fields']['equipo']+'</option>';
				});
			$('#id_equipo option').remove();
			if(option_equipos===''){
				 option_equipos='<option value="">---------</option>'
				}
			$('#id_equipo').append(option_equipos);
			$("#modal_cargando").modal("hide");
			llenar_input_equipo();
		});

		request.fail(function ( jqXHR, textStatus){
			// Redirecciona a una pagina general de error...
			$(location).attr('href','/general/NotFound');
		});
    };


    return{
        init:function () {
          handle_event();
          llenar_input_equipo();
          desabilitar_btn_eliminar();
        }
    }
}();