<style type="text/css">
${css}
</style>
%for object in objects:
<%page expression_filter="entity"/>

<table class="list_table">
    <caption>${ _(u"Bank reconciliation statement on account {code} {name}, dated {date}").format(
                    code=object.account_id.code, name=object.account_id.name, date=formatLang(object.period_id.date_stop, date=True)
             ) }</caption>
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
    %if object.print_unreconciled:
        <tr class="categ"><td colspan="6">${ _(u"Unreconciled Lines")}</td></tr>
        %for line in object.unreconciled_line_ids:
        <tr class="line">
            <td>${line.date}</td>
            <td>${line.ref or ''}</td>
            <td>${line.name or ''}</td>
            <td class="amount">${formatLang(line.debit_curr)}</td>
            <td class="amount">${formatLang(line.credit_curr)}</td>
            <td class="amount">${formatLang(line.amount_currency)}</td>
        </tr>
        %endfor
    %endif
    %if object.print_reconciled:
        <tr class="categ"><td colspan="6">${ _(u"Reconciled Lines")}</td></tr>
        %for line in object.reconciled_line_ids:
        <tr class="line">
            <td>${line.date}</td>
            <td>${line.ref or ''}</td>
            <td>${line.name or ''}</td>
            <td class="amount">${formatLang(line.debit_curr)}</td>
            <td class="amount">${formatLang(line.credit_curr)}</td>
            <td class="amount">${formatLang(line.amount_currency)}</td>
        </tr>
        %endfor
    %endif
    </tbody>
    <tfoot class="totals">
        <tr class="categ"><td colspan="6">${ _(u"Totals")}</td></tr>
        <tr>
            <td colspan="3"><b>${ _(u"Unreconciled Lines Total:") }</b></td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.unreconciled_total_debit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.unreconciled_total_credit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.unreconciled_total_balance) }</td>
        </tr>
        <tr>
            <td colspan="3"><b>${ _(u"Reconciled Lines Total:") }</b></td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.reconciled_total_debit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.reconciled_total_credit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.reconciled_total_balance) }</td>
        </tr>
        <tr>
            <td colspan="3"><b>${ _(u"Reconstituted Account Total:") }</b></td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.both_total_debit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.both_total_credit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.both_total_balance) }</td>
        </tr>
        <tr>
            <td colspan="3"><b>${ _(u"Control Account Total:") }</b></td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.control_total_debit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.control_total_credit) }</td>
            <td class="amount" style="white-space:nowrap">${ formatLang(object.control_total_balance) }</td>
        </tr>
        <tr>
            <td colspan="3"><b>${ _(u"Theoretical Account Balance:") }</b></td>
            <td colspan="3" class="amount" style="white-space:nowrap">${ formatLang(object.theoretical_balance) }</td>
        </tr>
    </tfoot>
</table>
%endfor
