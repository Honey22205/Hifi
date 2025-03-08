function trackOrder() {
    const container = document.querySelector('.order-detail-container');
    const orderId = container.getAttribute('data-order-id');
    const steps = document.querySelectorAll('.tracking-step');
    const progress = document.querySelector('.progress');
  
    // Send POST request to update the order's status
    fetch(`/api/orders/${orderId}/update_status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw err; });
      }
      return response.json();
    })
    .then(data => {
      // Determine the current status and update the UI accordingly.
      // Assume the status sequence is: Accepted, Picked Up, Out for Delivery, Delivered
      const statusOrder = ["Accepted", "Picked Up", "Out for Delivery", "Delivered"];
      
      // Map backend status if necessary (if backend returns "Completed" for final step)
      let displayStatus = data.delivery_status;
      if (displayStatus === "Completed") {
        displayStatus = "Delivered";
      }
      
      // Find the index of the current status
      const currentStep = statusOrder.indexOf(displayStatus);
      
      // Update the active class on each tracking step
      steps.forEach((step, index) => {
        if (index <= currentStep) {
          step.classList.add("active");
        } else {
          step.classList.remove("active");
        }
      });
      
      // Update progress bar width: calculates percentage based on current step
      progress.style.width = `${((currentStep + 1) / statusOrder.length) * 100}%`;
      
      // Optionally update any status text on the page if needed
      const statusElement = document.getElementById('orderStatus');
      if (statusElement) {
        statusElement.textContent = displayStatus;
      }
      
      // Optionally, if delivered and earnings data is provided, show an alert with earnings info
      if (displayStatus === "Delivered" && data.earnings) {
        alert(`Earnings Updated:
  Base Pay: ₹${data.earnings.base_pay}
  Bonus: ₹${data.earnings.bonus}
  Trips: ${data.earnings.trips_count}
  Total: ₹${data.earnings.total}`);
      }
    })
    .catch(err => {
      console.error('Error updating order status:', err);
      alert(err.error || 'An error occurred while updating status.');
    });
  }
  