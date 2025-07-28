// Pathway Pharmacy POS System - JavaScript

class PathwayPOS {
    constructor() {
        this.cart = {
            items: [],
            customer_id: null,
            discount_amount: 0,
            tax_rate: 12.5 // Ghana VAT rate
        };
        this.sessionId = this.generateSessionId();
        this.currency = {
            code: 'GHS',
            symbol: '₵',
            name: 'Ghana Cedis'
        };
        this.heldTransactions = [];
        this.init();
    }

    generateSessionId() {
        return 'pos_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.bindEvents();
        this.loadProducts();
        this.updateCartDisplay();
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('product-search');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(this.searchProducts.bind(this), 300));
        }

        // Barcode scanner simulation (Enter key)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target === searchInput) {
                e.preventDefault();
                this.searchByBarcode(searchInput.value);
            }
        });

        // Cart action buttons
        document.getElementById('clear-cart')?.addEventListener('click', this.clearCart.bind(this));
        document.getElementById('checkout-btn')?.addEventListener('click', this.showCheckoutModal.bind(this));
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async loadProducts(query = '') {
        try {
            const url = query ? `/api/products/search?q=${encodeURIComponent(query)}` : '/api/products?limit=20';
            const response = await fetch(url);
            const products = await response.json();
            this.displayProducts(products);
        } catch (error) {
            console.error('Error loading products:', error);
            this.showAlert('Error loading products', 'danger');
        }
    }

    async searchProducts(event) {
        const query = event.target.value.trim();
        if (query.length >= 2) {
            await this.loadProducts(query);
        } else if (query.length === 0) {
            await this.loadProducts();
        }
    }

    async searchByBarcode(barcode) {
        if (!barcode.trim()) return;

        try {
            const response = await fetch(`/api/products/barcode/${encodeURIComponent(barcode)}`);
            if (response.ok) {
                const product = await response.json();
                await this.addToCart(product.id, 1);
                document.getElementById('product-search').value = '';
            } else {
                this.showAlert('Product not found', 'warning');
            }
        } catch (error) {
            console.error('Error searching by barcode:', error);
            this.showAlert('Error searching product', 'danger');
        }
    }

    displayProducts(products) {
        const container = document.getElementById('product-grid');
        if (!container) return;

        container.innerHTML = products.map(product => `
            <div class="product-card" onclick="pos.addToCart(${product.id}, 1)">
                <div class="product-name">${this.escapeHtml(product.name)}</div>
                <div class="product-details">
                    SKU: ${this.escapeHtml(product.sku)}
                    ${product.generic_name ? `<br>Generic: ${this.escapeHtml(product.generic_name)}` : ''}
                    ${product.strength ? `<br>Strength: ${this.escapeHtml(product.strength)}` : ''}
                </div>
                <div class="product-price">${this.formatCurrency(product.selling_price)}</div>
                ${product.requires_prescription ? '<div class="prescription-required">Rx Required</div>' : ''}
            </div>
        `).join('');
    }

    async addToCart(productId, quantity = 1) {
        try {
            // Check if item already exists in cart
            const existingItem = this.cart.items.find(item => item.product_id === productId);
            
            if (existingItem) {
                existingItem.quantity += quantity;
            } else {
                // Fetch product details
                const response = await fetch(`/api/products/${productId}`);
                const product = await response.json();
                
                this.cart.items.push({
                    product_id: productId,
                    product_name: product.name,
                    sku: product.sku,
                    quantity: quantity,
                    unit_price: parseFloat(product.selling_price),
                    discount_amount: 0
                });
            }

            this.updateCartDisplay();
            this.showAlert(`Added ${quantity} item(s) to cart`, 'success');
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showAlert('Error adding item to cart', 'danger');
        }
    }

    removeFromCart(productId) {
        this.cart.items = this.cart.items.filter(item => item.product_id !== productId);
        this.updateCartDisplay();
    }

    updateQuantity(productId, quantity) {
        const item = this.cart.items.find(item => item.product_id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = quantity;
                this.updateCartDisplay();
            }
        }
    }

    updateCartDisplay() {
        const cartContainer = document.getElementById('cart-items');
        const cartSummary = document.getElementById('cart-summary');
        
        if (!cartContainer || !cartSummary) return;

        // Display cart items
        cartContainer.innerHTML = this.cart.items.map(item => {
            const lineTotal = item.quantity * item.unit_price - item.discount_amount;
            return `
                <div class="cart-item">
                    <div class="item-details">
                        <div class="item-name">${this.escapeHtml(item.product_name)}</div>
                        <div class="item-price">${this.formatCurrency(item.unit_price)} each</div>
                        <div class="quantity-controls">
                            <button class="quantity-btn" onclick="pos.updateQuantity(${item.product_id}, ${item.quantity - 1})">-</button>
                            <input type="number" class="quantity-input" value="${item.quantity}" 
                                   onchange="pos.updateQuantity(${item.product_id}, parseInt(this.value))">
                            <button class="quantity-btn" onclick="pos.updateQuantity(${item.product_id}, ${item.quantity + 1})">+</button>
                        </div>
                    </div>
                    <div class="item-actions">
                        <div class="item-total">${this.formatCurrency(lineTotal)}</div>
                        <button class="btn btn-sm btn-danger" onclick="pos.removeFromCart(${item.product_id})">Remove</button>
                    </div>
                </div>
            `;
        }).join('');

        // Calculate totals
        const subtotal = this.cart.items.reduce((sum, item) => 
            sum + (item.quantity * item.unit_price - item.discount_amount), 0);
        const taxAmount = (subtotal - this.cart.discount_amount) * this.cart.tax_rate / 100;
        const total = subtotal - this.cart.discount_amount + taxAmount;

        // Display summary
        cartSummary.innerHTML = `
            <div class="summary-row">
                <span>Subtotal:</span>
                <span>${this.formatCurrency(subtotal)}</span>
            </div>
            ${this.cart.discount_amount > 0 ? `
                <div class="summary-row">
                    <span>Discount:</span>
                    <span>-${this.formatCurrency(this.cart.discount_amount)}</span>
                </div>
            ` : ''}
            <div class="summary-row">
                <span>VAT (${this.cart.tax_rate}%):</span>
                <span>${this.formatCurrency(taxAmount)}</span>
            </div>
            <div class="summary-row total">
                <span>Total:</span>
                <span>${this.formatCurrency(total)}</span>
            </div>
        `;

        // Update checkout button state
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.disabled = this.cart.items.length === 0;
        }
    }

    clearCart() {
        this.cart.items = [];
        this.cart.customer_id = null;
        this.cart.discount_amount = 0;
        this.updateCartDisplay();
        this.showAlert('Cart cleared', 'info');
    }

    showCheckoutModal() {
        if (this.cart.items.length === 0) {
            this.showAlert('Cart is empty', 'warning');
            return;
        }

        // Create and show checkout modal
        const modal = this.createCheckoutModal();
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    createCheckoutModal() {
        const subtotal = this.cart.items.reduce((sum, item) => 
            sum + (item.quantity * item.unit_price - item.discount_amount), 0);
        const taxAmount = (subtotal - this.cart.discount_amount) * this.cart.tax_rate / 100;
        const total = subtotal - this.cart.discount_amount + taxAmount;

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Checkout</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="checkout-summary">
                        <h4>Order Summary</h4>
                        <div class="summary-row">
                            <span>Subtotal:</span>
                            <span>${this.formatCurrency(subtotal)}</span>
                        </div>
                        <div class="summary-row">
                            <span>VAT (${this.cart.tax_rate}%):</span>
                            <span>${this.formatCurrency(taxAmount)}</span>
                        </div>
                        <div class="summary-row total">
                            <span>Total:</span>
                            <span>${this.formatCurrency(total)}</span>
                        </div>
                    </div>
                    <div class="payment-section">
                        <h4>Payment Method</h4>
                        <select id="payment-method" class="form-control" onchange="pos.updatePaymentFields()">
                            <option value="cash">Cash</option>
                            <option value="mobile_money">Mobile Money</option>
                            <option value="card">Card (Visa/Mastercard)</option>
                            <option value="bank_transfer">Bank Transfer</option>
                            <option value="insurance">Insurance</option>
                            <option value="credit">Store Credit</option>
                        </select>
                        <div id="mobile-money-details" style="display: none; margin-top: 1rem;">
                            <label>Mobile Money Provider</label>
                            <select id="momo-provider" class="form-control">
                                <option value="mtn">MTN Mobile Money</option>
                                <option value="vodafone">Vodafone Cash</option>
                                <option value="airteltigo">AirtelTigo Money</option>
                            </select>
                            <label style="margin-top: 0.5rem;">Phone Number</label>
                            <input type="tel" id="momo-phone" class="form-control" placeholder="0XX XXX XXXX">
                        </div>
                        <div class="amount-section">
                            <label for="amount-paid">Amount Paid:</label>
                            <input type="number" id="amount-paid" class="form-control"
                                   value="${total.toFixed(2)}" step="0.01" min="${total.toFixed(2)}"
                                   placeholder="Amount in ${this.currency.code}">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="pos.processCheckout()">Complete Sale</button>
                </div>
            </div>
        `;

        return modal;
    }

    async processCheckout() {
        const paymentMethod = document.getElementById('payment-method').value;
        const amountPaid = parseFloat(document.getElementById('amount-paid').value);
        
        const subtotal = this.cart.items.reduce((sum, item) => 
            sum + (item.quantity * item.unit_price - item.discount_amount), 0);
        const taxAmount = (subtotal - this.cart.discount_amount) * this.cart.tax_rate / 100;
        const total = subtotal - this.cart.discount_amount + taxAmount;

        if (amountPaid < total) {
            this.showAlert('Insufficient payment amount', 'danger');
            return;
        }

        try {
            // In a real implementation, this would call the POS API
            // For now, we'll simulate the transaction
            const saleData = {
                items: this.cart.items,
                payment_method: paymentMethod,
                amount_paid: amountPaid,
                total: total,
                change: amountPaid - total
            };

            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Generate receipt data
            const receiptData = {
                saleNumber: `POS${Date.now()}`,
                items: this.cart.items,
                subtotal: subtotal,
                discount_amount: this.cart.discount_amount,
                tax_amount: taxAmount,
                total: total,
                payment_method: paymentMethod,
                amount_paid: amountPaid,
                change_given: amountPaid - total,
                cashier: 'Current User',
                customer: this.cart.customer_id ? { name: 'Customer Name' } : null
            };

            // Print receipt if enabled
            if (window.receiptGenerator) {
                window.receiptGenerator.printReceipt(receiptData);
            }

            // Clear cart and close modal
            this.clearCart();
            document.querySelector('.modal').remove();

            this.showAlert(`Sale completed! Change: ${this.formatCurrency(amountPaid - total)}`, 'success');
            
        } catch (error) {
            console.error('Error processing checkout:', error);
            this.showAlert('Error processing sale', 'danger');
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            ${message}
            <button class="close-btn" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }

    createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatCurrency(amount) {
        return `${this.currency.symbol}${parseFloat(amount).toFixed(2)}`;
    }

    // Hold Transaction functionality
    holdTransaction() {
        if (this.cart.items.length === 0) {
            this.showAlert('Cart is empty', 'warning');
            return;
        }

        const transactionId = `HOLD_${Date.now()}`;
        this.heldTransactions.push({
            id: transactionId,
            cart: JSON.parse(JSON.stringify(this.cart)),
            timestamp: new Date()
        });

        this.clearCart();
        this.showAlert(`Transaction held as ${transactionId}`, 'success');
        this.updateHeldTransactionsDisplay();
    }

    updateHeldTransactionsDisplay() {
        // This would update a UI element showing held transactions
        console.log('Held transactions:', this.heldTransactions);
    }

    // Customer Modal functionality
    showCustomerModal() {
        const modal = this.createCustomerModal();
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    createCustomerModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add Customer</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>First Name</label>
                        <input type="text" id="customer-first-name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Last Name</label>
                        <input type="text" id="customer-last-name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="customer-phone" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="customer-email" class="form-control">
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="pos.addCustomer()">Add Customer</button>
                </div>
            </div>
        `;
        return modal;
    }

    async addCustomer() {
        const firstName = document.getElementById('customer-first-name').value;
        const lastName = document.getElementById('customer-last-name').value;
        const phone = document.getElementById('customer-phone').value;
        const email = document.getElementById('customer-email').value;

        if (!firstName || !lastName) {
            this.showAlert('First name and last name are required', 'danger');
            return;
        }

        try {
            // In a real implementation, this would call the customer API
            const customerData = {
                first_name: firstName,
                last_name: lastName,
                phone: phone,
                email: email
            };

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));

            document.querySelector('.modal').remove();
            this.showAlert('Customer added successfully', 'success');
        } catch (error) {
            this.showAlert('Error adding customer', 'danger');
        }
    }

    // Discount Modal functionality
    showDiscountModal() {
        if (this.cart.items.length === 0) {
            this.showAlert('Cart is empty', 'warning');
            return;
        }

        const modal = this.createDiscountModal();
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    createDiscountModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Apply Discount</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Discount Type</label>
                        <select id="discount-type" class="form-control" onchange="pos.toggleDiscountInput()">
                            <option value="percentage">Percentage (%)</option>
                            <option value="amount">Fixed Amount (${this.currency.symbol})</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label id="discount-label">Discount Percentage</label>
                        <input type="number" id="discount-value" class="form-control" min="0" max="100" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Reason</label>
                        <select id="discount-reason" class="form-control">
                            <option value="senior_citizen">Senior Citizen Discount</option>
                            <option value="staff">Staff Discount</option>
                            <option value="loyalty">Loyalty Discount</option>
                            <option value="promotion">Promotional Discount</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="pos.applyDiscount()">Apply Discount</button>
                </div>
            </div>
        `;
        return modal;
    }

    toggleDiscountInput() {
        const type = document.getElementById('discount-type').value;
        const label = document.getElementById('discount-label');
        const input = document.getElementById('discount-value');

        if (type === 'percentage') {
            label.textContent = 'Discount Percentage';
            input.max = '100';
            input.placeholder = 'Enter percentage (0-100)';
        } else {
            label.textContent = `Discount Amount (${this.currency.symbol})`;
            input.max = '';
            input.placeholder = 'Enter amount';
        }
    }

    applyDiscount() {
        const type = document.getElementById('discount-type').value;
        const value = parseFloat(document.getElementById('discount-value').value);
        const reason = document.getElementById('discount-reason').value;

        if (!value || value <= 0) {
            this.showAlert('Please enter a valid discount value', 'danger');
            return;
        }

        const subtotal = this.cart.items.reduce((sum, item) =>
            sum + (item.quantity * item.unit_price - item.discount_amount), 0);

        if (type === 'percentage') {
            if (value > 100) {
                this.showAlert('Percentage cannot exceed 100%', 'danger');
                return;
            }
            this.cart.discount_amount = (subtotal * value / 100);
        } else {
            if (value > subtotal) {
                this.showAlert('Discount amount cannot exceed subtotal', 'danger');
                return;
            }
            this.cart.discount_amount = value;
        }

        this.cart.discount_reason = reason;
        this.updateCartDisplay();
        document.querySelector('.modal').remove();
        this.showAlert(`${type === 'percentage' ? value + '%' : this.formatCurrency(value)} discount applied`, 'success');
    }

    updatePaymentFields() {
        const paymentMethod = document.getElementById('payment-method').value;
        const mobileMoneyDetails = document.getElementById('mobile-money-details');

        if (paymentMethod === 'mobile_money') {
            mobileMoneyDetails.style.display = 'block';
        } else {
            mobileMoneyDetails.style.display = 'none';
        }
    }
}

// Initialize POS system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pos = new PathwayPOS();
});

// Add modal styles
const modalStyles = `
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background: white;
        border-radius: 8px;
        max-width: 500px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .modal-body {
        padding: 1.5rem;
    }
    
    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        padding: 1.5rem;
        border-top: 1px solid #e2e8f0;
    }
    
    .close-btn {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: #64748b;
    }
    
    .form-control {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .checkout-summary {
        margin-bottom: 2rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 8px;
    }
    
    .amount-section {
        margin-top: 1rem;
    }
`;

// Inject modal styles
const styleSheet = document.createElement('style');
styleSheet.textContent = modalStyles;
document.head.appendChild(styleSheet);
