# utils/print_invoice.py
from .helpers import format_currency
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import tkinter.messagebox as messagebox
from datetime import datetime
import db.queries as queries
from decimal import Decimal

class PrintInvoice:
    def __init__(self, sign_id):
        self.sign_id = sign_id
        self.sign_data = queries.get_sign_by_id(sign_id)
        self.components = queries.get_components_by_sign_id(sign_id)
        
    def generate_invoice(self):
        """Generate an invoice PDF file for the sign"""
        if not self.sign_data:
            messagebox.showerror("Error", "Sign data not found.")
            return False
            
        # Create filename based on sign name and date
        sanitized_name = ''.join(c if c.isalnum() else '_' for c in self.sign_data['SignName'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Invoice_{sanitized_name}_{timestamp}.pdf"
        
        # Create directory for invoices if it doesn't exist
        invoices_dir = "invoices"
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)
            
        filepath = os.path.join(invoices_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create content
        elements = []
        
        # Add title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,  # Center alignment
            spaceAfter=20
        )
        elements.append(Paragraph("Cotizacion de carteles ICAM81", title_style))
         
        # Add company info
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        elements.append(Paragraph("Impresiones ICAM81<br/>20 de Noviembre 1960<br/>La Paz, BCS.<br/>Cel: 612 157 1483", company_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add invoice details
        invoice_data = [
            ["Fecha de cotizacion:", datetime.now().strftime("%Y-%m-%d")],
            ["Cartel:", self.sign_data['SignName']],
            ["Cliente:", self.sign_data['CustomerInfo']],
            ["Estado:", self.sign_data['Status']],
            ["Creado:", self.sign_data['CreationDate'].strftime("%Y-%m-%d") if self.sign_data['CreationDate'] else "N/A"]
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add description if available
        if self.sign_data['Description']:
            elements.append(Paragraph("<b>Detalles:</b>", styles['Normal']))
            elements.append(Paragraph(self.sign_data['Description'], styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add components and jobs
        elements.append(Paragraph("<b>Detalles del trabajo:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        total_amount = Decimal('0.0')  # Use Decimal instead of float
        
        for component in self.components:
            # Component header
            elements.append(Paragraph(f"<b>{component['ComponentName']}</b>", styles['Normal']))
            
            # Get jobs for this component
            jobs = queries.get_jobs_by_component_id(component['ComponentID'])
            
            if jobs:
                # Create jobs table
                jobs_data = [["Componente", "Precio unitario", "Cantidad", "Monto"]]
                component_total = Decimal('0.0')  # Use Decimal instead of float
                
                for job in jobs:
                    quantity = job['Quantity'] if job['Quantity'] is not None else "-"
                    # Convert Amount to Decimal or 0 if None
                    amount = Decimal(str(job['Amount'])) if job['Amount'] is not None else Decimal('0.0')
                    
                    jobs_data.append([
                        job['JobName'],
                        f"${float(job['UnitCost']):.2f}",  # Convert for display
                        str(quantity),
                        f"${float(amount):.2f}" if amount else "-"  # Convert for display
                    ])
                    
                    component_total += amount
                
                # Add component total - use Paragraph for HTML formatting
                jobs_data.append([
                    "",
                    "",
                    Paragraph("<b>Total:</b>", styles['Normal']), 
                    Paragraph(f"<b>${float(component_total):.2f}</b>", styles['Normal'])
                ])
                
                jobs_table = Table(jobs_data, colWidths=[2.5*inch, 1.25*inch, 1.25*inch, 1.25*inch])
                jobs_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                    ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                    ('GRID', (0, 1), (-1, -2), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(jobs_table)
                elements.append(Spacer(1, 0.2*inch))
                
                total_amount += component_total
            else:
                elements.append(Paragraph("No jobs for this component.", styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        
        # Add grand total - use Paragraph for HTML formatting
        elements.append(Spacer(1, 0.2*inch))
        total_table = Table([
            [
                "",
                "",
                Paragraph("<b>GRAND TOTAL:</b>", styles['Normal']),
                Paragraph(f"<b>${float(total_amount):.2f}</b>", styles['Normal'])
            ]
        ], colWidths=[2.5*inch, 1.25*inch, 1.25*inch, 1.25*inch])
        
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (2, 0), (-1, 0), 'RIGHT'),
            ('BACKGROUND', (2, 0), (-1, 0), colors.lightgrey),
            ('LINEBELOW', (2, 0), (-1, 0), 1, colors.black),
            ('LINEABOVE', (2, 0), (-1, 0), 1, colors.black),
        ]))
        elements.append(total_table)
        
        # Add footer
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph("Thank you for your business!", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        return filepath
    
    def print_invoice(self):
        """Generate the invoice and open it"""
        try:
            filepath = self.generate_invoice()
            
            if filepath and os.path.exists(filepath):
                messagebox.showinfo("Success", f"Invoice generated successfully!\nSaved to: {filepath}")
                
                # Open the PDF file with the default PDF viewer
                os.startfile(filepath)
                return True
        except Exception as e:
            messagebox.showerror("Error", f"Error generating invoice: {e}")
        
        return False