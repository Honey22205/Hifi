document.addEventListener('DOMContentLoaded', function() {
    const orderData = {
        orderId: 'HF12345',
        orderTime: '2025-03-04 14:30',
        status: 'Ordered',
        estimatedDelivery: '30:00',
        customer: {
            name: 'Swastika gond',
            phone: '+1 (555) 123-4567',
            address: 'BIET,Jhansi'
        },
        items: [
            { name: 'HiFi Signature Burger', quantity: 2, price: 15.99 },
            { name: 'Truffle Parmesan Fries', quantity: 1, price: 7.99 },
            { name: 'Artisanal Lemonade', quantity: 2, price: 4.99 },
            { name: 'Gourmet Chocolate Brownie', quantity: 1, price: 6.99 }
        ],
        deliveryFee: 2.99,
        taxRate: 0.08
    };

    // Populate order details
    document.getElementById('orderStatus').textContent = orderData.status;
    document.getElementById('orderTime').textContent = orderData.orderTime;
    document.getElementById('estimatedDelivery').textContent = orderData.estimatedDelivery;
    document.getElementById('customerName').textContent = orderData.customer.name;
    document.getElementById('customerPhone').textContent = orderData.customer.phone;
    document.getElementById('customerAddress').textContent = orderData.customer.address;

    // Populate order items
    const itemList = document.getElementById('itemList');
    let subtotal = 0;
    orderData.items.forEach(item => {
        const li = document.createElement('li');
        const itemTotal = item.quantity * item.price;
        subtotal += itemTotal;
        li.innerHTML = `
            <span>${item.name} x${item.quantity}</span>
            <span>₹${itemTotal.toFixed(2)}</span>
        `;
        itemList.appendChild(li);
    });

    // Calculate and update order summary
    const tax = subtotal * orderData.taxRate;
    const total = subtotal + orderData.deliveryFee + tax;

    document.getElementById('subtotal').textContent = `₹${subtotal.toFixed(2)}`;
    document.getElementById('deliveryFee').textContent = `₹${orderData.deliveryFee.toFixed(2)}`;
    document.getElementById('tax').textContent = `₹${tax.toFixed(2)}`;
    document.getElementById('orderTotal').textContent = `₹${total.toFixed(2)}`;

    // Button functionality
    const acceptBtn = document.getElementById('acceptBtn');
    const completeBtn = document.getElementById('completeBtn');
    const orderStatus = document.getElementById('orderStatus');

    acceptBtn.addEventListener('click', function() {
        orderStatus.textContent = 'On the Way';
        orderStatus.style.backgroundColor = 'var(--primary-color)';
        this.disabled = true;
        completeBtn.disabled = false;
        startDeliveryTimer();
    });

    completeBtn.addEventListener('click', function() {
        orderStatus.textContent = 'Delivered';
        orderStatus.style.backgroundColor = 'var(--success-color)';
        this.disabled = true;
        stopDeliveryTimer();
    });

    // Delivery timer functionality
    let timerInterval;
    function startDeliveryTimer() {
        let time = 30 * 60; // 30 minutes in seconds
        const estimatedDelivery = document.getElementById('estimatedDelivery');
        
        timerInterval = setInterval(() => {
            const minutes = Math.floor(time / 60);
            const seconds = time % 60;
            estimatedDelivery.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (time <= 0) {
                clearInterval(timerInterval);
                estimatedDelivery.textContent = "Delivery Overdue";
                estimatedDelivery.style.color = 'var(--danger-color)';
            }
            time--;
        }, 1000);
    }

    function stopDeliveryTimer() {
        clearInterval(timerInterval);
        document.getElementById('estimatedDelivery').textContent = "Delivered";
    }
});