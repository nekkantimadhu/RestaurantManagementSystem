// Notify when an order is placed for the chef
document.getElementById("orderForm").addEventListener("submit", function(event) {
    event.preventDefault();
    alert("Order placed! Chef has been notified.");
    // Simulate chef notification with a delay for preparation
    setTimeout(function() {
        notifyStaff("The food is ready to be served!");
    }, 10000); // Assume it takes 10 minutes to prepare the food
});

function notifyStaff(message) {
    let notificationArea = document.getElementById("notificationArea");
    let notification = document.createElement("div");
    notification.className = "notification";
    notification.innerHTML = message;
    notificationArea.appendChild(notification);
}
