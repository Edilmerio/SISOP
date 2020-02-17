let Pago = function () {

    let suf_name_fields = {'enlace': 'enlace', 'tipo_sistema':'tipo_sistema_n', 'valor_total': 'valor_total',
        'fecha_inicio_pago': 'fecha_inicio_pago', 'meses_diferir': 'meses_diferir'};

    let init_typeahead = function(){
        let $e_aux;
        let data_sistemas;
        $('.typeahead').typeahead({
            autoSelect: true,
            minLength: 2,
            delay: 400,
            items: 'all',
            source: function (query, process) {
                $e_aux = $(this.$element[0]);
                if (!(query && query.trim().length)){
                    $e_aux.val('');
                    return [];
                }
                return $.ajax({
                    url: '/espectro/lista_sistemas_pago_licencias',
                    data: {q: ((query.substring('|') !== -1) ? query.split('|')[0] : query )},
                    // data: {q: query},
                    dataType: 'json',
                    beforeSend: function() {
                    //that.$element is a variable that stores the element the plugin was called on
                        $e_aux.addClass('loading-spinner1');
                    },
                    complete: function() {
                        $e_aux.removeClass('loading-spinner1');
                    }
                })
                    .done(function(response) {
                        data_sistemas = response[1];
                        return process (response[0]);
                    });
            },
            matcher: function (item) {
                // let sist = item.name.split('|')[0];
                // let sist_lower_case = sist.toLowerCase();
                // let q_lower_case = this.query.indexOf('|')!==-1? this.query.toLowerCase().split('|')[0] : this.query.toLowerCase();
                // return (sist_lower_case.indexOf(q_lower_case) !== -1)
                let fields_sistemas = '[id^="id_form-"][id$="-sistema"]';
                let id_element_tepeahead = this.$element[0].id;
                let flag = true;
                $(fields_sistemas).each(function () {
                    if (item.name === $(this).val() && $(this).attr('id') !== id_element_tepeahead){
                        flag = false;
                    }
                });
                return flag;
            },
            highlighter: function (item) {
                // let s = item.split('|')[0];
                // let ind = s.indexOf(this.query);
                // return s.substring(0, ind) + "<strong>" + s.substring(ind, ind  + this.query.length) + "</strong>"
                //     + s.substring(ind  + this.query.length) + '|' + item.split('|')[1]
                return item
            },            
            afterSelect: function (item) {
                let sist = data_sistemas[item.id];
                if (sist){
                    let pre_fix = $e_aux.attr('id').substring(0, $e_aux.attr('id').indexOf('sistema'));
                    for (let key in suf_name_fields) {
                    // check if the property/key is defined in the object itself,
                        if (sist.hasOwnProperty(suf_name_fields[key])) {
                            $('#' + pre_fix + key).val(sist[suf_name_fields[key]]);
                        }
                    }
                }
            }

        })
    };

    //check sistema
    let check_sistema = function () {
        let $this = $(this);
        let ul_sibling = $this.siblings('ul.typeahead');
        if (ul_sibling.length === 0 || ul_sibling.css('display') === 'none'){
            let text_li_active = ul_sibling.children('li.active').text();
            if (text_li_active !== $this.val()){
                // let pre_fix = $this.attr('id').substring(0, $e_aux.attr('id').indexOf('sistema'));
                let pre_fix = $this.attr('id').substring(0, $this.attr('id').indexOf('sistema'));
                for (let key in suf_name_fields) {
                    $('#' + pre_fix + key).val('');
                }
                Base.notificacion('error/Error/El sistema ' +
                    $this.val()  + ' no existe..');
            }
        }
    };
    //valida los campos del pago.
    let validate_fields = function() {
        let is_valid = true;
        let required_fields = [['#id_no_notificacion'], ['#id_fecha_notificacion', '#calendar_fecha_notificacion'],
            ['#id_valor_total'],['[id^="id_form-"][id$="-sistema"]'], ['[id^="id_form-"][id$="-enlace"]'],
            ['[id^="id_form-"][id$="-tipo_sistema"]'], ['[id^="id_form-"][id$="-valor_total"]'],
            ['[id^="id_form-"][id$="-meses_diferir"]'],
            ['[id^="id_form-"][id$="-fecha_inicio_pago"]','[id^="dp_f_i-form-"]']];
        let gt0_fields = [['#id_valor_total'], ['[id^="id_form-"][id$="-valor_total"]'], ['[id^="id_form-"][id$="-meses_diferir"]']];

        let validate_required = function (fields) {
            $.each(elem_and_element_notify(fields), function (index, value) {
                if (!ValidateFields.required($(value[0]), $(value[1]), 'Este campo es obligatorio.'))
                    is_valid = false;
            })
        };

        let validate_gt = function(fields, v){
            $.each(elem_and_element_notify(fields), function (index, value) {
                if (!ValidateFields.gt($(value[0]), $(value[1]), v, `Campo mayor ${v}`))
                    is_valid = false;
            })
        };

        // funcion que devulve elementos Jquery
        //con el padre despues del cual se van a poner
        //la notify
        let elem_and_element_notify = function(elements){
            let $elements_and_elements_notify = [];
            $.each(elements, function (index, value) {
                let $elements = $(value[0]);
                $elements.each(function() {
                    let $elem_notify = (value[1] === undefined) ? $(this) : $(this).parents(value[1]);
                    $elements_and_elements_notify.push([$(this), $elem_notify]);
                })
            });
            return $elements_and_elements_notify;
        };

        validate_required(required_fields);
        validate_gt(gt0_fields, 0);
        return is_valid
    };


    let init = function () {
        init_typeahead();
    };

    return{
        init: init,
        init_typeahead: init_typeahead,
        check_sistema: check_sistema,
        validate_fields: validate_fields
    };
}();