import ast
import json
import time
from datetime import datetime
from typing import Dict

from src.invoice_creator import simplify_invoice_data, create_invoice_pdf, generate_invoice_number
from src.transformer import create_line_items, entities_response

def prepare_page_data(page_url):
    response = []
    for i in range(len(page_url)):
        datastruct = {
              "id": 0,
              "pageNumber": i + 1,
              "page_image_url": page_url[i],
              "dimension": {
                "width": 2048,
                "height": 2651,
                "unit": "pixels"
              }
        }
        response.append(datastruct)
    return response



# def additional_charges_data(additional_charges_ds):
#     "additional_charges_datastructures"
#     return None


def get_doc_id():
    return "ca75acd7-93b1-4230-b95c-7f2f0031bcac"


def get_org_id():
    return "da295928-a147-4f4d-abfc-9de385985d23"


def process_invoice_from_json(input_json_path: str):
    """Process invoice_output data from JSON input instead of Streamlit forms"""
    # Load the input JSON
    with open(input_json_path, 'r') as f:
        input_data = json.load(f)

    moc_data = input_data.get('moc_data', {})
    line_items = input_data.get('line_items', [])

    additional_charges_ds = {
        "freight_charges": input_data['freight_charges'],
        "handling_charges": input_data['handling_charges'],
        "shipping_charges": input_data['shipping_charges']
    }

    # Fill in any missing data with defaults
    moc_data, total_tax_amount = prepare_moc_data(moc_data)
    page_details = prepare_page_data(input_data['moc_data']['page_image_url'])
    # additional_charges = additional_charges_data(additional_charges_ds)

    # Process line items
    processed_line_items = []
    for i, item in enumerate(line_items):
        processed_line_items.append(process_line_item(i, item))

    # Create response
    resp_json = read_data()
    litms = []
    for i, line_item in enumerate(processed_line_items):
        litms.append(create_line_items(resp_json[0]['document']['line_items'][0], i, **line_item))

    resp_json[0]['document']['entities'] = entities_response(resp_json[0]['document']['entities'], moc=moc_data)
    resp_json[0]['document']['line_items'] = litms
    resp_json[0]['document']['pages'] = page_details
    resp_json[0]['document']['taxes'][0]['entities'][1]['value']['inferred_value'] = moc_data['tax_rate']
    resp_json[0]['document']['taxes'][0]['entities'][2]['text'] = total_tax_amount

    resp_json[0]['document']['doc_id'] = get_doc_id()
    resp_json[0]['document']['org_id'] = get_org_id()
    resp_json[0]['document']['processed_at'] = time.time()

    # # Save input json for reference
    # mock = {"moc_data": moc_data, "line_items": processed_line_items}
    # with open('input_json.json', 'w') as f:
    #     json.dump(mock, f)

    # Generate invoice_output
    invoice_data = simplify_invoice_data(moc_data, processed_line_items)
    invoice_number = create_invoice_pdf(invoice_data['simplified_invoice_data'], processed_line_items)
    resp_json[0]['document']['file_name'] = f"invoice_{invoice_number}.pdf"
    resp_json[0]['document']['entities'][0]['text'] = invoice_number
    resp_json[0]['document']['entities'][0]['value']['inferred_value'] = invoice_number
    resp_json[0]['document']['entities'][0]['value']['normalized_val'] = invoice_number
    print(f"invoice Number generated {invoice_number}")
    return resp_json, invoice_number


def prepare_moc_data(moc_data: Dict):
    """Prepare MOC data with defaults for any missing fields"""
    defaults = {
        "supplier_name": "MARCELA NUNEZ",
        "supplier_address": "123 Supplier Street",
        "supplier_city": "New York",
        "supplier_state": "NY",
        "supplier_country": "USA",
        "supplier_postal_code": "10001",
        "supplier_po_box": "PO Box 456",
        "receiver_name": "John Doe",
        "receiver_city": "Los Angeles",
        "receiver_state": "CA",
        "receiver_country": "USA",
        "receiver_postal_code": "90001",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": datetime.now().strftime("%Y-%m-%d"),
        "po_id": "980jn324",
        "payment_term": "NET 30",
        "currency": "USD",
        "net_amount": "515.0",
        "discount_rate": "10",
        "tax_rate": "10"
    }

    # Fill in any missing fields with defaults
    for key, value in defaults.items():
        if key not in moc_data or not moc_data[key]:
            moc_data[key] = value

    # Convert string values to appropriate types for calculations
    net_amount = float(moc_data["net_amount"])
    tax_rate = float(moc_data["tax_rate"])
    discount_rate = float(moc_data["discount_rate"])

    # Calculate derived fields
    discount_amount = net_amount * tax_rate / 100
    gross_amount = net_amount + (net_amount * tax_rate / 100)
    total_tax_amount = gross_amount - net_amount

    # Add calculated fields
    moc_data.update({
        "total_tax_amount": str(total_tax_amount),
        "discount_amount": str(discount_amount),
        "total_amount_due": str((net_amount + total_tax_amount) - discount_amount),
        "doc_id": moc_data.get("doc_id", "asfdsdfsdfsdf-sd-f-sd-f-sd-f-sdf"),
        "org_id": moc_data.get("org_id", "a000395-jsdfn-asdfsadf-asd-c-sdc"),
        "processed_at": moc_data.get("processed_at", str(int(datetime.now().timestamp())))
    })

    return moc_data, total_tax_amount


def process_line_item(index: int, item: Dict) -> Dict:
    """Process a line item with defaults for any missing fields"""
    defaults = {
        "name": f"Widget {index + 1}",
        "description": f"A very useful widget #{index + 1}",
        "quantity": 10,
        "currency": "USD",
        "unit_price": 15.00,
        "unit_of_measurement": "each",
        "discount_rate": 10,
        "total_tax_amount": 105
    }

    # Fill in any missing fields with defaults
    for key, value in defaults.items():
        if key not in item or item[key] == "":
            item[key] = value

    # Calculate derived fields
    quantity = float(item["quantity"])
    unit_price = float(item["unit_price"])
    discount_rate = float(item["discount_rate"])
    total_tax_amount = float(item["total_tax_amount"])

    net_amount = quantity * unit_price
    discount_amount = (net_amount + total_tax_amount)
    gross_amount = net_amount + (net_amount + total_tax_amount)
    total_tax_amount = gross_amount - net_amount

    # Add calculated fields
    item.update({
        "net_amount": net_amount,
        "gross_amount": gross_amount,
        "purchase_order": item.get("purchase_order", f"PO"),
        "discount_amount": discount_amount,
        "total_tax_amount": total_tax_amount
    })

    return item

def read_data():
    with open("sample_res.txt", "r", encoding="utf-8") as file:
        data = json.loads(parse_json_string(file.read()))
    return data

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


def main():
    """Main function to process invoice_output from JSON"""
    # Path to input JSON file
    input_json_path = 'invoice_input.json'


    # Process the invoice_output
    response_json, invoice_number = process_invoice_from_json(input_json_path)

    with open(f'mock_idp_response/response_{invoice_number}.json', 'w') as f:
        json.dump(response_json, f)
    print(f"Processing complete. Response saved to 'response_{invoice_number}.json'")


if __name__ == "__main__":
    main()