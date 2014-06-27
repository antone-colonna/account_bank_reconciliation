<style type="text/css">
${css}
</style>
%for object in objects:
<%page expression_filter="entity"/>

<table class="list_table">
    <caption>${ _(u"Bank reconciliation session on account {code} {name}, dated {date}").format(
                    code=object.account_id.code, name=object.account_id.name, date=formatLang(object.period_id.date_stop, date=True
             )) }</caption>
    <thead>
        <tr>
            <th>${ _(u"Date") }</th>
            <th>${ _(u"Reference") }</th>
            <th>${ _(u"Name") }</th>
            <th>${ _(u"Credit") }</th>
            <th>${ _(u"Debit") }</th>
            <th>${ _(u"Balance") }</th>
        </tr>
    </thead>
    <tbody>
    %for line in object.line_ids:
        <tr class="line">
            <td>${line.date or ''}</td>
            <td>${line.ref or ''}</td>
            <td>${line.move_line_id.name}</td>
            <td class="amount">${formatLang(line.debit_curr)}</td>
            <td class="amount">${formatLang(line.credit_curr)}</td>
            <td class="amount">${formatLang(line.amount_currency)}</td>
        </tr>
    %endfor
    </tbody>
    <tfoot class="totals">
        <tr>
            <td colspan="3"><b>${ _(u"Total:") }</b></td>
            <td class="amount" style="white-space:nowrap">${ formatLang(sum(line.debit_curr for line in object.line_ids)) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(sum(line.credit_curr for line in object.line_ids)) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.total_amount) }</td>
        </tr>
    </tfoot>
</table>
%endfor
