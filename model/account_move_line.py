from openerp.osv import osv, fields


class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    def _one2one_fnct(self, cr, uid, ids, field_name, args, context=None):

        related_model = self.fields_get(
            cr, uid, allfields=[field_name], context=context
        )[field_name]['relation']
        related_field = args[0] if isinstance(args, (list, tuple)) else args
        related_osv = self.pool[related_model]
        domain = [(related_field, 'in', ids)]
        res_ids = related_osv.search(cr, uid, domain, context=context)

        if len(ids) == 1:
            return {ids[0]: res_ids[0] if res_ids else False}
        else:
            vals = related_osv.read(
                cr, uid, res_ids, [related_field], context=context
            )
            res = dict.fromkeys(ids, False)
            for val in vals:
                res[val[related_field][0]] = val['id']
            return res

    def _reconciliation_line_id_store(self, cr, uid, ids, context=None):
        vals = self.read(cr, uid, ids, ['move_line_id'], context=context)
        return [val['move_line_id'][0] for val in vals]

    _columns = {
        'reconciliation_line_id': fields.function(
            _one2one_fnct,
            arg='move_line_id',
            type='many2one',
            obj='account.bank.reconciliation.line',
            string="Reconciliation Line",
            readonly=True,
            store={
                'account.bank.reconciliation.line': (
                    _reconciliation_line_id_store,
                    ['move_line_id'],
                    10
                )
            }
        )
    }
