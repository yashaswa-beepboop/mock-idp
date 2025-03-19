import json
import ast

def parse_json_string(json_string):
    for parser in [
        lambda x: json.loads(x),
        lambda x: json.loads(ast.literal_eval(x)),
        lambda x: json.loads(x.encode('utf-8').decode('unicode-escape'))
    ]:
        try:
            return parser(json_string)
        except (json.JSONDecodeError, ValueError, SyntaxError):
            continue
    raise ValueError("Unable to parse JSON string")

def read_data():
    with open("sample_res.txt", "r", encoding="utf-8") as file:
        data = json.loads(parse_json_string(file.read()))
    return data

## line items
def create_line_items(df,
                      index,
                      name,
                      description,
                      quantity,
                      currency,
                      unit_price,
                      unit_of_measurement,
                      net_amount,
                      gross_amount,
                      purchase_order,
                      discount_amount,
                      discount_rate,
                      total_tax_amount):

    df["index"] = int(index)

    df["name"] = name
    df["entities"][1]['text'] = name
    df["entities"][1]['value']['inferred_value'] = name
    df["entities"][1]['value']['normalized_val'] = name

    #description
    df["entities"][2]['text'] = description
    df["entities"][2]['value']['normalized_val'] = description
    df["entities"][2]['value']['normalized_val'] = description

    # product_code
    # quantity
    df["entities"][4]['text'] = str(quantity)
    df["entities"][4]['value']['inferred_value'] = str(quantity)

    # unit_price
    df["entities"][5]['text'] = str(unit_price)
    df["entities"][5]['value']['inferred_value'] = str(unit_price)
    df["entities"][5]['value']['currency'] = str(currency)

    # unit_of_measurement
    df["entities"][6]['text'] = unit_of_measurement
    df["entities"][6]['value']['inferred_value'] = unit_of_measurement
    df["entities"][6]['value']['normalized_val'] = unit_of_measurement

    # net_amount
    df["entities"][7]['text'] = net_amount
    df["entities"][7]['value']['inferred_value'] = net_amount
    df["entities"][7]['value']['currency'] = str(currency)

    # gross_amount
    df["entities"][8]['text'] = gross_amount
    df["entities"][8]['value']['inferred_value'] = gross_amount
    df["entities"][8]['value']['currency'] = str(currency)

    # purchase_order
    df["entities"][9]['text'] = str(purchase_order)
    df["entities"][9]['value']['inferred_value'] = str(purchase_order)
    df["entities"][9]['value']['normalized_val'] = str(purchase_order)

    if discount_amount:
        # discount_amount
        df["entities"][10]['text'] = str(discount_amount)
        df["entities"][10]['value']['inferred_value'] = str(discount_amount)
        df["entities"][10]['value']['currency'] = str(currency)

    if discount_rate:
        # discount_rate
        df["entities"][11]['text'] = str(discount_rate)
        df["entities"][11]['value']['inferred_value'] = str(discount_rate)

    if total_tax_amount:
        # total_tax_amount
        df["entities"][12]['text'] = str(total_tax_amount)
        df["entities"][12]['value']['inferred_value'] = str(total_tax_amount)
        df["entities"][12]['value']['currency'] = str(currency)

    return df

def page_response(df, id, pageNumber, page_image_url):
    df["id"] = id
    df["pageNumber"] = pageNumber
    df["page_image_url"] = page_image_url

    return df

def entities_response(df, moc):
    df[1]['text'] = moc['invoice_date']
    df[1]['value']['inferred_value'] = moc['invoice_date']
    df[1]['value']['normalized_val'] = moc['invoice_date']

    # supplier name
    df[2]['text'] = moc['supplier_name']
    df[2]['value']['inferred_value'] = moc['supplier_name']
    df[2]['value']['normalized_val'] = moc['supplier_name']

    # supplier address
    df[3]['text'] = moc['supplier_address']
    df[3]['value']['inferred_value'] = moc['supplier_address']
    df[3]['value']['normalized_val']['city'] = moc['supplier_city']
    df[3]['value']['normalized_val']['state'] = moc['supplier_state']
    df[3]['value']['normalized_val']['country'] = moc['supplier_country']

    df[3]['value']['config_dict']['city'] = moc['supplier_city']
    df[3]['value']['config_dict']['state'] = moc['supplier_state']
    df[3]['value']['config_dict']['country'] = moc['supplier_country']
    df[3]['value']['config_dict']['postal_code'] = moc['supplier_postal_code']

    df[3]['value']['normalized_val_dict']['city'] = moc['supplier_city']
    df[3]['value']['normalized_val_dict']['state'] = moc['supplier_state']
    df[3]['value']['normalized_val_dict']['country'] = moc['supplier_country']
    df[3]['value']['normalized_val_dict']['postal_code'] = moc['supplier_postal_code']

    # receiver_name
    df[18]['text'] = moc['receiver_name'] = moc['receiver_name']
    df[18]['value']['inferred_value'] = moc['receiver_name']
    df[18]['value']['normalized_val'] = moc['receiver_name']

    df[19]['text'] = moc['receiver_name']
    df[19]['value']['inferred_value'] = moc['receiver_name']
    df[19]['value']['normalized_val']['city'] = moc['receiver_city']
    df[19]['value']['normalized_val']['state'] = moc['receiver_state']
    df[19]['value']['normalized_val']['country'] = moc['receiver_country']
    df[19]['value']['normalized_val']['postal_code'] = moc['receiver_postal_code']

    df[19]['value']['config_dict']['city'] = moc['supplier_city']
    df[19]['value']['config_dict']['state'] = moc['supplier_state']
    df[19]['value']['config_dict']['country'] = moc['supplier_country']
    df[19]['value']['config_dict']['postcode'] = moc['supplier_postal_code']

    df[19]['value']['normalized_val_dict']['city'] = moc['supplier_po_box']
    df[19]['value']['normalized_val_dict']['state'] = moc['supplier_state']
    df[19]['value']['normalized_val_dict']['country'] = moc['supplier_country']
    df[19]['value']['normalized_val_dict']['postal_code'] = moc['supplier_postal_code']

    # po_id
    df[39]['text'] = moc['po_id']
    df[39]['value']['inferred_value'] = moc['po_id']
    df[39]['value']['normalized_val'] = moc['po_id']

    # payment_terms
    df[40]['text'] = moc['payment_term']

    #  due_date
    df[41]['text'] = moc['due_date']
    df[41]['value']['inferred_value'] = moc['due_date']
    df[41]['value']['normalized_val'] = moc['due_date']

    df[46]['text'] = '$' + moc['total_tax_amount']
    df[46]['value']['inferred_value'] = '$' + moc['total_tax_amount']
    df[46]['value']['normalized_val'] = moc['total_tax_amount']  # no $ sign required
    df[46]['value']['currency'] = moc['currency']

    # net_amount
    df[47]['text'] = '$' + moc['net_amount']
    df[47]['value']['inferred_value'] = '$' + moc['net_amount']
    df[47]['value']['normalized_val'] = moc['net_amount']  # no $ sign required
    df[47]['value']['currency'] = moc['currency']

    # gross_amount
    df[48]['text'] = '$' + moc['net_amount']
    df[48]['value']['inferred_value'] = '$' + moc['net_amount']
    df[48]['value']['normalized_val'] = moc['net_amount']  # no $ sign required
    df[47]['value']['currency'] = moc['currency']

    df[49]['text'] = moc['currency']

    # currency_exchange_rate
    # total_discount_amount
    df[51]['text'] = '$' + moc['discount_amount']
    df[51]['value']['inferred_value'] = '$' + moc['net_amount']
    df[51]['value']['normalized_val'] = moc['net_amount']  # no $ sign required
    df[51]['value']['currency'] = moc['currency']

    # discount_rate
    df[53]['text'] = moc['discount_rate']
    df[53]['value']['inferred_value'] = moc['discount_rate']
    df[53]['value']['normalized_val'] = moc['discount_rate']

    # total_amount_due
    df[56]['text'] = '$' + moc['total_amount_due']
    df[56]['value']['inferred_value'] = '$' + moc['total_amount_due']
    df[56]['value']['normalized_val'] = moc['total_amount_due']

    return df

