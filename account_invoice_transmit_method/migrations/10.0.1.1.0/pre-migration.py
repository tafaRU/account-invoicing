# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Migrate customer_invoice_transmit_method_id
    # from res.partner to ir.property
    if not version:
        return

    # Get all companies
    cr.execute('SELECT id FROM res_company')
    companies = cr.fetchall()

    # Get partners with customer transmit method set
    cr.execute(
        'SELECT id, customer_invoice_transmit_method_id '
        'FROM res_partner '
        'WHERE customer_invoice_transmit_method_id IS NOT NULL '
    )
    customer_partners = cr.fetchall()

    # Get partners with supplier transmit method set
    cr.execute(
        'SELECT id, supplier_invoice_transmit_method_id '
        'FROM res_partner '
        'WHERE supplier_invoice_transmit_method_id IS NOT NULL'
    )
    supplier_partners = cr.fetchall()

    # Get the correct reference fields
    cr.execute(
        "SELECT id FROM ir_model WHERE model = 'res.partner'"
    )
    partner_model = cr.fetchone()

    # Customer transmit method field
    cr.execute(
        "SELECT id FROM ir_model_fields WHERE "
        "name = 'customer_invoice_transmit_method_id'"
        "AND model_id = '%s'" % partner_model[0]
    )

    customer_invoice_transmit_method_id_field = cr.fetchone()

    # Supplier transmit method field
    cr.execute(
        "SELECT id FROM ir_model_fields WHERE "
        "name = 'supplier_invoice_transmit_method_id'"
        "AND model_id = '%s'" % partner_model[0]
    )

    supplier_invoice_transmit_method_id_field = cr.fetchone()

    keys = [
        'create_uid',
        'write_uid',
        'create_date',
        'write_date',
        'company_id',
        'fields_id',
        'name',
        'res_id',
        'value_reference',
        'type',
    ]

    superuser_id = '1'  # String-type for join

    lines = list()
    for company in companies:
        # Property lines for customer_invoice_transmit_method_id
        for partner in customer_partners:
            lines.append([
                superuser_id,
                superuser_id,
                'NOW()',
                'NOW()',
                '%s' % company[0],  # company id
                '%s' % customer_invoice_transmit_method_id_field[0],
                "'customer_invoice_transmit_method_id'",
                "'res.partner,%s'" % partner[0],  # partner id
                "'transmit.method,%s'" % partner[1],  # transmit method id
                "'many2one'",
            ])

        # Property lines for supplier_invoice_transmit_method_id
        for partner in supplier_partners:
            lines.append([
                superuser_id,
                superuser_id,
                'NOW()',
                'NOW()',
                '%s' % company[0],  # company id
                '%s' % supplier_invoice_transmit_method_id_field[0],
                "'supplier_invoice_transmit_method_id'",
                "'res.partner,%s'" % partner[0],  # partner id
                "'transmit.method,%s'" % partner[1],  # transmit method id
                "'many2one'",
            ])

        # Construct and execute the query
        if lines:
            sql = list()
            sql.append("INSERT INTO %s (" % 'ir_property')
            sql.append(", ".join(keys))
            sql.append(") VALUES ")
            for line_values in lines:
                sql.append("(")
                sql.append(", ".join(line_values))
                sql.append("),")

            # Strip the last comma
            sql[-1] = sql[-1].rstrip(',')

            sql.append(";")

            sql_query = "".join(sql)
            cr.execute(sql_query)
