import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
import random
import string


def simplify_invoice_data(moc_data, line_items):
    # Simplify supplier address
    supplier_full_address = (f"{moc_data['supplier_address']} "
                             f"{moc_data['supplier_city']} "
                             f"{moc_data['supplier_state']} "
                             f"{moc_data['supplier_country']} "
                             f"{moc_data['supplier_postal_code']}")

    # Simplify receiver address
    receiver_full_address = (f"{moc_data['receiver_name']} "
                             f"{moc_data['receiver_city']} "
                             f"{moc_data['receiver_state']} "
                             f"{moc_data['receiver_country']} "
                             f"{moc_data['receiver_postal_code']}")

    # Simplify the main invoice_output data
    simplified_invoice_data = {
        "invoice_date": moc_data["invoice_date"],
        "supplier_name": moc_data["supplier_name"],
        "supplier_full_address": supplier_full_address,
        "receiver_full_address": receiver_full_address,
        "payment_term": moc_data["payment_term"],
        "due_date": moc_data["due_date"],
        "currency": moc_data["currency"],
        "net_amount": moc_data["net_amount"],
        "total_tax_amount": moc_data["total_tax_amount"],
        "discount_amount": moc_data["discount_amount"],
        "discount_rate": moc_data["discount_rate"],
        "total_amount_due": moc_data["total_amount_due"],
        "doc_id": moc_data["doc_id"],
        "org_id": moc_data["org_id"],
        "processed_at": moc_data["processed_at"]
    }

    # Simplify line items
    simplified_line_items = [
        {
            "name": item["name"],
            "description": item["description"],
            "quantity": item["quantity"],
            "currency": item["currency"],
            "unit_price": item["unit_price"],
            "total_tax_amount": item["total_tax_amount"]
        } for item in line_items
    ]

    return {"simplified_invoice_data": simplified_invoice_data, "line_items": simplified_line_items}

def generate_invoice_number():
    """Generate a random invoice_output number"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def create_invoice_pdf(invoice_data, line_items):
    invoice_number = generate_invoice_number()
    doc = SimpleDocTemplate(
        f"invoice_output/invoice_{invoice_number}.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    ))
    styles.add(ParagraphStyle(
        name='CompanyInfo',
        fontSize=12,
        spaceAfter=6,
        textColor=colors.HexColor('#34495e')
    ))

    # Content elements
    elements = []

    # Header
    elements.append(Paragraph("INVOICE", styles['CustomTitle']))

    # Company Information
    supplier_info = f"""
    <b>{invoice_data['supplier_name']}</b><br/>
    {invoice_data['supplier_full_address']}
    """
    elements.append(Paragraph(supplier_info, styles['CompanyInfo']))
    elements.append(Spacer(1, 20))

    # Bill To
    bill_to = f"""
    <b>Bill To:</b><br/>
    {invoice_data['receiver_full_address']}
    """
    elements.append(Paragraph(bill_to, styles['CompanyInfo']))
    elements.append(Spacer(1, 20))

    invoice_details = [
        ['Invoice Number:', invoice_number],
        ['Invoice Date:', invoice_data['invoice_date']],
        ['Due Date:', invoice_data['due_date']],
        ['Payment Terms:', invoice_data['payment_term']],
        ['Document ID:', invoice_data['doc_id']]
    ]

    invoice_table = Table(invoice_details, colWidths=[2 * inch, 2 * inch])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))

    # Line Items
    line_item_data = [['Item', 'Description', 'Quantity', 'Unit Price', 'Tax', 'Total']]

    for item in line_items:
        total = item['quantity'] * item['unit_price']
        line_item_data.append([
            item['name'],
            item['description'],
            str(item['quantity']),
            f"${item['unit_price']:.2f}",
            f"${item['total_tax_amount']:.2f}",
            f"${(total + item['total_tax_amount']):.2f}"
        ])

    line_items_table = Table(line_item_data,
                             colWidths=[1.5 * inch, 2 * inch, 0.8 * inch, 1 * inch, 0.8 * inch, 1 * inch])
    line_items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(line_items_table)
    elements.append(Spacer(1, 20))

    # Summary
    summary_data = [
        ['Net Amount:', f"${float(invoice_data['net_amount']):.2f}"],
        ['Tax Amount:', f"${float(invoice_data['total_tax_amount']):.2f}"],
        ['Discount:', f"${float(invoice_data['discount_amount']):.2f} ({invoice_data['discount_rate']}%)"],
        ['Total Amount Due:', f"${float(invoice_data['total_amount_due']):.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 1.5 * inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -2), colors.HexColor('#7f8c8d')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)

    # Build the PDF
    doc.build(elements)

    return invoice_number