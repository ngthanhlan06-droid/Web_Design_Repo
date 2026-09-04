function renderUsers(users) {
    let tableBody = document.querySelector("#user-table tbody");
    tableBody.innerHTML = "";

    users.forEach((user) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.phone}</td>
            <td>${user.email}</td>
            <td>${user.website}</td>
            <td>${user.address.city}</td>`;
        tableBody.appendChild(row);
    });
}

async function fetchUsers() {
    try {
        const response = await fetch("https://jsonplaceholder.typicode.com/users");
        const users = await response.json();
        renderUsers(users);
    } catch (error) {
        console.error("Lỗi khi lấy dữ liệu:", error);
    }
}