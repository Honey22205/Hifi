function handleAccept(userId) {
    const row = document.getElementById(`user-${userId}`);
    const acceptedTable = document.getElementById("acceptedAgentsList");
    acceptedTable.appendChild(row);
    row.removeChild(row.lastElementChild); // Remove actions column after acceptance
    alert(`User ID ${userId} accepted.`);
}

function handleReject(userId) {
    alert(`User ID ${userId} rejected.`);
    document.getElementById(`user-${userId}`).remove();
}