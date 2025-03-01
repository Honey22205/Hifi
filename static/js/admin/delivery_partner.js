function handleAccept(userId) {
    fetch(`/admin/accept/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const row = document.getElementById(`user-${userId}`);
        const acceptedTable = document.getElementById("acceptedAgentsList");
        acceptedTable.appendChild(row);
        row.removeChild(row.lastElementChild); // Remove actions column after acceptance
        // alert(data.message);
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        // alert('There was an error processing the acceptance.');
        window.location.reload();
    });
}

function handleReject(userId) {
    fetch(`/admin/reject/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // alert(data.message);
        document.getElementById(`user-${userId}`).remove();
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        // alert('There was an error processing the rejection.');
        window.location.reload();
    });
}

function handleDeactivate(userId) {
    fetch(`/admin/deactivate/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Optionally, display a success message:
        // alert(data.message);
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        // Optionally, display an error message:
        // alert('There was an error processing the deactivation.');
        window.location.reload();
    });
}

function handleActivate(userId) {
    fetch(`/admin/activate/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Optionally, display a success message:
        // alert(data.message);
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        // Optionally, display an error message:
        // alert('There was an error processing the activation.');
        window.location.reload();
    });
}

// Helper function to show the custom confirmation modal
function showConfirmationPopup(message, onConfirm, onCancel) {
    const modal = document.getElementById('confirmationModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmBtn = document.getElementById('confirmBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const closeModal = document.getElementById('closeModal');
  
    modalMessage.textContent = message;
    modal.style.display = 'block';
  
    // Clear previous event handlers by replacing the element if needed
    confirmBtn.onclick = function () {
      modal.style.display = 'none';
      onConfirm();
    };
  
    cancelBtn.onclick = function () {
      modal.style.display = 'none';
      if (onCancel) onCancel();
    };
  
    // Allow clicking the "x" to cancel
    closeModal.onclick = function () {
      modal.style.display = 'none';
      if (onCancel) onCancel();
    };
  
    // Optionally, close the modal if user clicks outside of it
    window.onclick = function (event) {
      if (event.target === modal) {
        modal.style.display = 'none';
        if (onCancel) onCancel();
      }
    };
  }
  
  function handleActivate(userId) {
    showConfirmationPopup("Are you sure you want to activate this delivery agent?", function () {
      // On confirm, send activation request
      fetch(`/admin/activate/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => window.location.reload())
      .catch(error => {
        console.error('Error:', error);
        window.location.reload();
      });
    });
  }
  
  function handleDeactivate(userId) {
    showConfirmationPopup("Are you sure you want to deactivate this delivery agent?", function () {
      // On confirm, send deactivation request
      fetch(`/admin/deactivate/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => window.location.reload())
      .catch(error => {
        console.error('Error:', error);
        window.location.reload();
      });
    });
  }
  
