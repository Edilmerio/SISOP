import django_tables2 as tables

class IndicadoresTable(tables.Table):
    nivel = tables.Column(verbose_name='Org.')
    lineas = tables.Column(verbose_name='Líneas')
    sum_pend = tables.Column(verbose_name='Pend')
    rep_total = tables.Column()
    demora_total = tables.Column(verbose_name='Dem Total')
    demora_prom = tables.Column(verbose_name='Dem Prom')
    sum_rep_lte_1d = tables.Column(verbose_name='Rep < 1d')
    por_ciento_rep_lte_1d = tables.Column(verbose_name='% Rep < 1d')
    sum_rep_lte_3d = tables.Column(verbose_name='1 < Rep < 3d')
    por_ciento_rep_lte_3d = tables.Column(verbose_name='% Rep < 3d')
    sum_rep_gt_3d = tables.Column(verbose_name='Rep > 3d')
    por_ciento_rep_gt_3d = tables.Column(verbose_name='% Rep > 3d')
    ri = tables.Column(verbose_name='RI')
    por_ciento_ri = tables.Column(verbose_name='% RI')
    disponibilidad = tables.Column('% Disp.')

    def __init__(self, *args, **kwargs):
        for _, val in self.base_columns.items():
            val.orderable = False
        super().__init__(*args, **kwargs)

    class Meta:
        attrs = {'class': 'table table-condensed table-hover table-bordered'}