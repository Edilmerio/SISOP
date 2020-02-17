var FormsetDjango = function () {

    var prefix;
    var elem_total_form;

    var init = function () {
      inicializar_variables();
      desabilitar_btn_eliminar();
    };
    var inicializar_variables = function () {
        prefix='form';
        elem_total_form = $('#id_' + prefix + '-TOTAL_FORMS');
    };
    var add_form_to_formset = function (form_clone, place_new_form, parent_formset, func) {
        // form_clone: form exixtente y que se quiere clonar
        // place_new_form: lugar a partir del cual se ubica el new form
        // parent_formset: elemnt parent of formset
        // func funcion a ejecutar
        var form_count = parseInt(elem_total_form.val());
        var form_cloned=$(form_clone.get(0)).clone();
        form_cloned.find('ul.errorlist').remove();
        form_cloned.find('ul.typeahead').remove();
        form_cloned.find(':input[type=text]').val('');
        form_cloned.find(':input[type=number]').val('');
        form_cloned.find('input[type=hidden]').remove();
		$(place_new_form).after(form_cloned);
		elem_total_form.val(form_count + 1);
		// $('#id_' + prefix + '-INITIAL_FORMS').val(form_count + 1);
		//$('.form-dinamico .delete-form').attr('disabled', false);
        if (func) func();
        actualizar_attr_elem_forms(parent_formset.children('.form-dinamico'));
    };

    var actualizar_attr_elem_forms =function($formset_django){
		var prefix='form';
		var id_regex = new RegExp('(' + prefix + '-\\d+)');
		// var form_count=$('.form-dinamico').length;
		$formset_django.each(function(index){
			var replacement = prefix + '-' + index;
			if($(this).attr('id')) $(this).attr('id',$(this).attr('id').replace(id_regex, replacement))

			$(this).find(':input').each(function(){
				if ($(this).attr('for')) $(this).attr('for', $(this).attr('for').replace(id_regex, replacement));
				if($(this).attr('id')) $(this).attr('id',$(this).attr('id').replace(id_regex, replacement));
				if($(this).attr('name')) $(this).attr('name',$(this).attr('name').replace(id_regex, replacement));
			});
		});
    };

    var delete_form_to_formset = function ($form_delete) {
        var prefix='form';
        if ($($form_delete).find('input[type=hidden]').length === 0 || $($form_delete).find('input[type=hidden]').val()==='' )
            $form_delete.remove();
        else{
            $form_delete.find('div.checker input[type=checkbox]').prop('checked', true);
            $form_delete.find('div.checker span').addClass('checked');
            $form_delete.css('display', 'none');
        }
        var forms = $('.form-dinamico');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        desabilitar_btn_eliminar();
        actualizar_attr_elem_forms(forms);
    };

    var desabilitar_btn_eliminar = function () {
        var forms = $('.form-dinamico');
        if( forms.filter(':visible').length===1)
            $('.form-dinamico .delete-form').attr('disabled', true);
    };

    return{
       init: init,
       add_form_to_formset: add_form_to_formset,
       delete_form_to_formset: delete_form_to_formset
    };
}();