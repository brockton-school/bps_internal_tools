// Redirect after 2 seconds (confirmation page)
function redirectConfToHome() {
    setTimeout(function() {
        window.location.href = "/";
    }, 5000);

    // Redirect back to the root when the user clicks anywhere on the screen
    document.body.addEventListener('click', function() {
        window.location.href = '/';
    });
}

// Show reason field if sign out or student sign in, and hide action buttons
function handleAction(action, userType, reasonNeeded) {
    var reasonField = document.getElementById("reason-field");
    var actionButtons = document.getElementById("action-buttons");
    var visitorReasonField = document.getElementById("visitor-reason");
    var header = document.getElementById("sign-in-out-header");

    // Set the action in the form and handle the display of the reason field
    document.getElementById('action-input').value = action;

    header.style.display = "none"; // Hide the main header

    // This conditional is a bit of a mess... refactor this shiz...

    if (userType === "Student" && action === "Signing Out") {
        reasonField.style.display = "block";
        actionButtons.style.display = "none";  // Hide the action buttons
    } else if (userType === "Staff" && action === "Signing Out" && reasonNeeded === "true") {
        reasonField.style.display = "block";
        actionButtons.style.display = "none";  // Hide the action buttons
    } else if (userType === "Visitor" && action === "Signing In") {
        visitorReasonField.style.display = "block";
        actionButtons.style.display = "none";  // Hide the Sign In/Out buttons

        // make visitor specific stuff required
        document.getElementById("visitor-reason-input").required = true;
        document.getElementById("visitor-phone-input").required = true;
    } else {
        reasonField.style.display = "none";
        document.getElementById('reason-input').value = ""; // Clear any existing reason
        document.forms['signForm'].submit();  // Automatically submit the form
        showLoadingIndicator();
    }
}

// Function to set the reason when a reason button is clicked
function setReason(reason) {
    document.getElementById('reason-input').value = reason;

    // Get form state
    var action = document.getElementById('action-input').value
    var userType = document.getElementById('user-type-input').value

    if (action === "Signing Out" && userType !== "Visitor") {
        // Hide the reason fields
        var reasonField = document.getElementById("reason-field");
        reasonField.style.display = "none";

        // Then ask for return time...
        var returnTime = document.getElementById("return-time");
        returnTime.style.display = "block";

    } else {
        // Otherwise just submit...
        document.forms['signForm'].submit();
        showLoadingIndicator();
    }
    
}

// Function to submit the form on Enter key in the "Other reason" input
function submitOnEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();  // Prevent the default form submission behavior
        const otherReason = document.getElementById('other-reason-input').value;
        setReason(otherReason);  // Set the reason and submit the form
    }
}

// Handle est return time

// Set the selected return time to the hidden input
function selectReturnTime(time) {
    document.getElementById('return-time-input').value = time;
    document.getElementById('custom-time').value = '';  // Clear custom time if a button is clicked
    document.forms['signForm'].submit();
    showLoadingIndicator();
}

// Set custom time to the hidden input when user selects a time
function selectCustomTime(time) {
    document.getElementById('return-time-input').value = time;
}

// Handle visitor info submission
function submitVisitorOnEnter(event) {
    if (event.key === "Enter") {
        document.forms['signForm'].submit();
        showLoadingIndicator();
    }
}

// show loading progress
function showLoadingIndicator() {
    const form = document.getElementById("signForm"); // Replace with your form ID
    const loadingIndicator = document.getElementById("loading-indicator");
    loadingIndicator.style.display = "block";
    form.style.display = "none"
}