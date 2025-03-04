// DOM Elements
const editToggleBtn = document.getElementById('edit-toggle-btn');
const cancelBtn = document.getElementById('cancel-btn');
const saveBtn = document.getElementById('save-btn');
const editButtons = document.getElementById('edit-buttons');
const profileForm = document.getElementById('profile-form');
const formInputs = profileForm.querySelectorAll('input, select, textarea');
const imageUploadBtn = document.getElementById('image-upload-btn');
const profileImageInput = document.getElementById('profile-image-input');
const profileImg = document.getElementById('profile-img');
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const toast = document.getElementById('toast');

// Display elements
const displayName = document.getElementById('display-name');
const displayEmail = document.getElementById('display-email');
const displayPhone = document.getElementById('display-phone');
// Guard against missing vehicle and preferred hours display elements
const displayVehicle = document.getElementById('display-vehicle'); // might be null if commented out
const displayArea = document.getElementById('display-area');
const displayHours = document.getElementById('display-hours'); // might be null if commented out

// Form elements
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const phoneInput = document.getElementById('phone');
// Guard for vehicle type and preferred hours if they exist
const vehicleTypeInput = document.getElementById('vehicleType'); 
const deliveryAreaInput = document.getElementById('deliveryArea');
const preferredHoursInput = document.getElementById('preferredHours');

let originalFormValues = {};

// Tab functionality
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons and contents
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(`${tabId}-tab`).classList.add('active');
    });
});

// Toggle edit mode
editToggleBtn.addEventListener('click', () => {
    const isEditing = editToggleBtn.textContent.trim() === 'Save';
    
    if (isEditing) {
        // Save changes
        saveChanges();
    } else {
        // Enter edit mode
        enableEditMode();
    }
});

// Cancel edit
cancelBtn.addEventListener('click', () => {
    disableEditMode();
    restoreOriginalValues();
});

// Save changes (also attached to saveBtn)
saveBtn.addEventListener('click', () => {
    saveChanges();
});

// Profile image upload
profileImageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            profileImg.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// Functions
function enableEditMode() {
    storeOriginalValues();
    formInputs.forEach(input => {
        input.disabled = false;
    });
    editButtons.classList.remove('hidden');
    imageUploadBtn.classList.remove('hidden');
    
    // Change edit button to "Save"
    editToggleBtn.innerHTML = `
        <svg class="btn-icon icon" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"></path>
        </svg>
        Save
    `;
}

function disableEditMode() {
    formInputs.forEach(input => {
        input.disabled = true;
    });
    editButtons.classList.add('hidden');
    imageUploadBtn.classList.add('hidden');
    
    // Change button back to "Edit"
    editToggleBtn.innerHTML = `
        <svg class="btn-icon icon" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"></path>
        </svg>
        Edit
    `;
}

function storeOriginalValues() {
    originalFormValues = {
        name: nameInput.value,
        email: emailInput.value,
        phone: phoneInput.value,
        deliveryArea: deliveryAreaInput.value,
        bio: document.getElementById('bio').value,
        available: document.getElementById('available').checked,
        profileImage: profileImg.src
    };
    if (vehicleTypeInput) {
        originalFormValues.vehicleType = vehicleTypeInput.value;
    }
    if (preferredHoursInput) {
        originalFormValues.preferredHours = preferredHoursInput.value;
    }
}

function restoreOriginalValues() {
    nameInput.value = originalFormValues.name;
    emailInput.value = originalFormValues.email;
    phoneInput.value = originalFormValues.phone;
    deliveryAreaInput.value = originalFormValues.deliveryArea;
    document.getElementById('bio').value = originalFormValues.bio;
    document.getElementById('available').checked = originalFormValues.available;
    profileImg.src = originalFormValues.profileImage;
    if (vehicleTypeInput && originalFormValues.vehicleType) {
        vehicleTypeInput.value = originalFormValues.vehicleType;
    }
    if (preferredHoursInput && originalFormValues.preferredHours) {
        preferredHoursInput.value = originalFormValues.preferredHours;
    }
}

function saveChanges() {
    displayName.textContent = nameInput.value;
    displayEmail.textContent = emailInput.value;
    displayPhone.textContent = phoneInput.value;
    if (vehicleTypeInput && displayVehicle) {
        displayVehicle.textContent = vehicleTypeInput.options[vehicleTypeInput.selectedIndex].text;
    }
    displayArea.textContent = deliveryAreaInput.value;
    if (preferredHoursInput && displayHours) {
        displayHours.textContent = preferredHoursInput.value;
    }
    
    disableEditMode();
    showToast();
}

function showToast() {
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Initialize vehicle type select if exists
if (vehicleTypeInput) {
    vehicleTypeInput.value = 'bike';
}
