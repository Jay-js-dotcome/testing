document.addEventListener("DOMContentLoaded", function () {
    // Initialize conversation history for each chatbot
    const conversationContexts = {
        chatbot1: [],
        chatbot2: [],
        chatbot3: [],
    };

    const chatMessages = document.getElementById("chatbox");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const chatForm = document.getElementById("chat-form");
    const selectedChatbotInput = document.getElementById("selected-chatbot");
    const chatbotButtons = document.querySelectorAll(".chatbot-button");

    let isPendingResponse = false; // Flag to track if a request is pending

    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();

        // Check if a request is pending; if so, return early
        if (isPendingResponse) {
            return;
        }

        const userMessage = userInput.value.trim();
        if (userMessage !== "") {
            const selectedChatbot = selectedChatbotInput.value;

            // Display user message in the conversation box
            displayMessage(userMessage, "user");

            // Add user message to the conversation history
            conversationContexts[selectedChatbot].push({ content: userMessage, role: "user" });

            // Disable chat input and chatbot switching while waiting for a response
            isPendingResponse = true;
            userInput.disabled = true;
            chatbotButtons.forEach((button) => {
                button.disabled = true;
            });

            // Send user message and selected chatbot to the server as JSON
            fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_input: userMessage,
                    selected_chatbot: selectedChatbot,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Display chatbot response in the conversation box
                    data.response.forEach((paragraph) => {
                        displayMessage(paragraph, "chatbot");
                    });

                    // Add chatbot response to the conversation history
                    data.response.forEach((paragraph) => {
                        conversationContexts[selectedChatbot].push({ content: paragraph, role: "chatbot" });
                    });

                    // Scroll to the bottom of the conversation box to show the latest messages
                    chatMessages.scrollTop = chatMessages.scrollHeight;

                    // Re-enable chat input and chatbot switching
                    isPendingResponse = false;
                    userInput.disabled = false;
                    chatbotButtons.forEach((button) => {
                        button.disabled = false;
                    });
                })
                .catch((error) => {
                    console.error("Error sending message:", error);

                    // Handle errors and re-enable chat input and chatbot switching
                    isPendingResponse = false;
                    userInput.disabled = false;
                    chatbotButtons.forEach((button) => {
                        button.disabled = false;
                    });
                });

            // Clear user input
            userInput.value = "";
        }
    });

    // Function to display a message in the conversation box
    function displayMessage(message, role) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", role + "-message");
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        chatMessages.appendChild(messageDiv);
    }

    // Add event listeners to switch between chatbots
    chatbotButtons.forEach((button) => {
        button.addEventListener("click", function () {
            // Check if a request is pending; if so, return early
            if (isPendingResponse) {
                return;
            }

            // Remove the 'active' class from all chatbot buttons
            chatbotButtons.forEach((btn) => {
                btn.classList.remove("active");
            });

            // Add the 'active' class to the clicked chatbot button
            this.classList.add("active");

            // Update the selected chatbot input
            const selectedChatbot = this.getAttribute("data-chatbot");
            selectedChatbotInput.value = selectedChatbot;

            // Clear the conversation box
            chatMessages.innerHTML = "";

            // Display the conversation history for the selected chatbot
            const conversationHistory = conversationContexts[selectedChatbot];
            conversationHistory.forEach((message) => {
                displayMessage(message.content, message.role);
            });

            // Scroll to the bottom of the conversation box to show the latest messages
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    });
});
