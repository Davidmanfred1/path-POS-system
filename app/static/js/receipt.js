// Receipt generation for Pathway Pharmacy POS System

class ReceiptGenerator {
    constructor() {
        this.pharmacyInfo = {
            name: "Pathway Pharmacy",
            address: "123 Main St, Accra, Ghana",
            phone: "+233 20 123 4567",
            license: "PH123456789",
            tin: "TIN: C0123456789",
            vat: "VAT REG: GL123456789"
        };
    }

    generateReceipt(saleData) {
        const receiptHtml = `
            <div class="receipt">
                <div class="receipt-header">
                    <div class="ghana-flag"></div>
                    <h2>${this.pharmacyInfo.name}</h2>
                    <p>${this.pharmacyInfo.address}</p>
                    <p>Tel: ${this.pharmacyInfo.phone}</p>
                    <p>License: ${this.pharmacyInfo.license}</p>
                    <p>${this.pharmacyInfo.tin}</p>
                    <p>${this.pharmacyInfo.vat}</p>
                </div>
                
                <div class="receipt-details">
                    <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                        <span>Receipt #: ${saleData.saleNumber}</span>
                        <span>${new Date().toLocaleDateString('en-GB')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                        <span>Time: ${new Date().toLocaleTimeString('en-GB')}</span>
                        <span>Cashier: ${saleData.cashier || 'System'}</span>
                    </div>
                    ${saleData.customer ? `
                        <div style="margin-bottom: 1rem;">
                            <strong>Customer:</strong> ${saleData.customer.name}<br>
                            ${saleData.customer.phone ? `Phone: ${saleData.customer.phone}<br>` : ''}
                            ${saleData.customer.loyaltyCard ? `Loyalty: ${saleData.customer.loyaltyCard}` : ''}
                        </div>
                    ` : ''}
                </div>

                <div class="receipt-items">
                    <div style="border-bottom: 1px dashed #000; margin: 1rem 0;"></div>
                    ${saleData.items.map(item => `
                        <div class="receipt-item">
                            <div style="font-weight: bold;">${item.product_name}</div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
                                <span>${item.quantity} x ₵${item.unit_price.toFixed(2)}</span>
                                <span>₵${(item.quantity * item.unit_price).toFixed(2)}</span>
                            </div>
                            ${item.discount_amount > 0 ? `
                                <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #666;">
                                    <span>Discount</span>
                                    <span>-₵${item.discount_amount.toFixed(2)}</span>
                                </div>
                            ` : ''}
                            ${item.prescription_number ? `
                                <div style="font-size: 0.8em; color: #666;">
                                    Rx: ${item.prescription_number}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                    <div style="border-bottom: 1px dashed #000; margin: 1rem 0;"></div>
                </div>

                <div class="receipt-totals">
                    <div style="display: flex; justify-content: space-between;">
                        <span>Subtotal:</span>
                        <span>₵${saleData.subtotal.toFixed(2)}</span>
                    </div>
                    ${saleData.discount_amount > 0 ? `
                        <div style="display: flex; justify-content: space-between;">
                            <span>Discount:</span>
                            <span>-₵${saleData.discount_amount.toFixed(2)}</span>
                        </div>
                    ` : ''}
                    <div style="display: flex; justify-content: space-between;">
                        <span>VAT (12.5%):</span>
                        <span>₵${saleData.tax_amount.toFixed(2)}</span>
                    </div>
                    <div class="receipt-total" style="display: flex; justify-content: space-between; font-weight: bold; font-size: 1.1em; border-top: 1px solid #000; padding-top: 0.5rem; margin-top: 0.5rem;">
                        <span>TOTAL:</span>
                        <span>₵${saleData.total.toFixed(2)}</span>
                    </div>
                </div>

                <div class="receipt-payment" style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>Payment Method:</span>
                        <span>${this.formatPaymentMethod(saleData.payment_method)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Amount Paid:</span>
                        <span>₵${saleData.amount_paid.toFixed(2)}</span>
                    </div>
                    ${saleData.change_given > 0 ? `
                        <div style="display: flex; justify-content: space-between;">
                            <span>Change:</span>
                            <span>₵${saleData.change_given.toFixed(2)}</span>
                        </div>
                    ` : ''}
                    ${saleData.payment_method === 'mobile_money' && saleData.momo_reference ? `
                        <div style="font-size: 0.9em; margin-top: 0.5rem;">
                            MoMo Ref: ${saleData.momo_reference}
                        </div>
                    ` : ''}
                </div>

                <div class="receipt-footer" style="text-align: center; margin-top: 1.5rem; font-size: 0.9em;">
                    <div style="border-bottom: 1px dashed #000; margin: 1rem 0;"></div>
                    <p><strong>Thank you for choosing Pathway Pharmacy!</strong></p>
                    <p>Your health is our priority</p>
                    <p style="font-size: 0.8em; margin-top: 1rem;">
                        For inquiries: ${this.pharmacyInfo.phone}<br>
                        Visit us: www.pathwaypharmacy.com.gh
                    </p>
                    <p style="font-size: 0.8em; margin-top: 1rem;">
                        Keep this receipt for returns/exchanges<br>
                        Valid for 30 days from purchase date
                    </p>
                    <div style="margin-top: 1rem; font-size: 0.8em;">
                        <p>Powered by Pathway POS System</p>
                        <p>${new Date().toISOString()}</p>
                    </div>
                </div>
            </div>
        `;

        return receiptHtml;
    }

    formatPaymentMethod(method) {
        const methods = {
            'cash': 'Cash',
            'mobile_money': 'Mobile Money',
            'card': 'Card Payment',
            'bank_transfer': 'Bank Transfer',
            'insurance': 'Insurance',
            'credit': 'Store Credit'
        };
        return methods[method] || method;
    }

    printReceipt(saleData) {
        const receiptHtml = this.generateReceipt(saleData);
        
        // Create a new window for printing
        const printWindow = window.open('', '_blank', 'width=400,height=600');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Receipt - ${saleData.saleNumber}</title>
                <style>
                    body {
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.4;
                        margin: 0;
                        padding: 10px;
                        background: white;
                    }
                    .receipt {
                        max-width: 300px;
                        margin: 0 auto;
                    }
                    .receipt-header {
                        text-align: center;
                        border-bottom: 1px dashed #000;
                        padding-bottom: 1rem;
                        margin-bottom: 1rem;
                    }
                    .receipt-header h2 {
                        margin: 0.5rem 0;
                        font-size: 16px;
                    }
                    .receipt-header p {
                        margin: 0.2rem 0;
                        font-size: 10px;
                    }
                    .ghana-flag {
                        background: linear-gradient(to right, #ce1126 33%, #fcd116 33%, #fcd116 66%, #006b3f 66%);
                        height: 4px;
                        width: 100%;
                        margin-bottom: 0.5rem;
                    }
                    .receipt-item {
                        margin-bottom: 0.5rem;
                        font-size: 11px;
                    }
                    @media print {
                        body { margin: 0; }
                        .receipt { max-width: none; }
                    }
                </style>
            </head>
            <body>
                ${receiptHtml}
                <script>
                    window.onload = function() {
                        window.print();
                        window.onafterprint = function() {
                            window.close();
                        };
                    };
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();
    }

    emailReceipt(saleData, email) {
        // In a real implementation, this would send the receipt via email
        console.log('Emailing receipt to:', email);
        alert(`Receipt would be emailed to ${email}`);
    }

    saveReceiptAsPDF(saleData) {
        // In a real implementation, this would generate and download a PDF
        console.log('Saving receipt as PDF');
        alert('PDF generation feature - to be implemented');
    }
}

// Global receipt generator instance
window.receiptGenerator = new ReceiptGenerator();
