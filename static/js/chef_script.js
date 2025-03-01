// Notify the chef when an order is placed
document.addEventListener('DOMContentLoaded', () => {
    const orderList = document.getElementById('order-list');
    
    // Example: After 5 seconds, a new order appears
    setTimeout(() => {
        let newOrder = document.createElement('div');
        newOrder.classList.add('order-card');
        newOrder.innerHTML = `
            <h3>Order #12346</h3>
            <p>Items: Burger, Fries</p>
            <p>Table: 7</p>
            <button class="mark-ready-btn">Mark as Ready</button>
        `;
        orderList.appendChild(newOrder);

        // Add functionality to mark as ready
        newOrder.querySelector('.mark-ready-btn').addEventListener('click', () => {
            alert('Order #12346 is ready to serve!');
            newOrder.style.backgroundColor = '#4CAF50'; // Change background to green once ready
        });

    }, 5000); // Delay for the simulated new order
});
