from flask import Flask, request, render_template, jsonify
import os
import replicate
import google.generativeai as palm
import os

app = Flask(__name__)

# Set Replicate API token
os.environ["REPLICATE_API_TOKEN"] = "r8_XORpj2GqeOjbDhB5wElpNGSDNLNGJQF16HaC7"

# Initialize conversation contexts for each chatbot
conversation_context_1 = {
    "user_message_history": [],
    "assistant_message_history": [],
}

conversation_context_2 = {
    "user_message_history": [],
    "assistant_message_history": [],
}

conversation_context_3 = {
    "user_message_history": [],
    "assistant_message_history": [],
}
# Function to interact with the original chatbot
def llama_chatbot(user_input, conversation_context):
    print(user_input)
    # Construct the prompt using an f-string
    pre_prompt = f"You are a helpful assistant like Siri from Apple, kindly help to answer the query from user: {user_input}"
    
    # Retrieve the conversation history for the chatbot
    user_message_history = conversation_context_1["user_message_history"]
    assistant_message_history = conversation_context_1["assistant_message_history"]
    
    # Add the user's message to the conversation history
    user_message_history.append(user_input)

    # Construct the conversation history for the prompt
    conversation_history = "\n".join(
        [f"User: {user_msg}\nAssistant: {assistant_msg}" for user_msg, assistant_msg in zip(user_message_history, assistant_message_history)]
    )
    # Generate chatbot response
    response = replicate.run(
        'meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d',
        input={"prompt": f"{pre_prompt}\n{conversation_history}\nUser: {user_input}\nAssistant:", "temperature": 3, "top_p": 0.5, "min_new_tokens": -1, "top_k": 50,
               "max_new_tokens": 1800, "repetition_penalty": 1}
    )
    
    # Join the response into a single string
    response_text = ''.join(response)
    
    # Split the response into paragraphs based on newline characters
    paragraphs = response_text.split('\n')
    
    # Remove empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    # Add the chatbot's response to the conversation history
    assistant_message_history.append(response_text)
    
    # Return the paragraphs as a list
    return paragraphs

# Function to interact with the new chatbot (chatbot v2)
def llama_chatbot_v2(user_input, conversation_context):
    print(user_input)
    # Construct the prompt using an f-string
    pre_prompt = f"You are a helpful assistant like Siri from Apple, kindly help to answer the query from user: {user_input}"
    
    # Retrieve the conversation history for the chatbot
    user_message_history = conversation_context_2["user_message_history"]
    assistant_message_history = conversation_context_2["assistant_message_history"]
    
    # Add the user's message to the conversation history
    user_message_history.append(user_input)
    
    # Construct the conversation history for the prompt
    conversation_history = "\n".join(
        [f"User: {user_msg}\nAssistant: {assistant_msg}" for user_msg, assistant_msg in zip(user_message_history, assistant_message_history)]
    )
    
    # Generate chatbot response
    response = replicate.run(
        'meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e',
        input={"prompt": f"{pre_prompt}\n{conversation_history}\nUser: {user_input}\nAssistant:", "temperature": 3, "top_p": 0.5, "min_new_tokens": -1, "top_k": 50,
               "max_new_tokens": 1800, "repetition_penalty": 1}
    )
    
    # Join the response into a single string
    response_text = ''.join(response)
    
    # Split the response into paragraphs based on newline characters
    paragraphs = response_text.split('\n')
    
    # Remove empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    # Add the chatbot's response to the conversation history
    assistant_message_history.append(response_text)
    
    # Return the paragraphs as a list
    return paragraphs


def palm_chatbot(user_input, conversation_context):
    try:
        print("inside palm")
        palm.configure(api_key="AIzaSyBwBbPto-g8kvpWrAe3cD_HhLnKrK-IQg4")


        # Retrieve the conversation history for the chatbot
        user_message_history = conversation_context_3["user_message_history"]
        assistant_message_history = conversation_context_3["assistant_message_history"]

        # Add the user's message to the conversation history
        user_message_history.append(user_input)

        # Construct the conversation history for the prompt
        conversation_history = "\n".join(
            [f"User: {user_msg}\nAssistant: {assistant_msg}" for user_msg, assistant_msg in zip(user_message_history, assistant_message_history)]
        )

        # Generate chatbot response using the palm_chatbot
        response = palm.generate_text(model="models/text-bison-001",prompt=f"You are the smartest man on earth and now your job is an assistant, this is the conversation history:{conversation_history}\nThis is prompt from user: {user_input}",temperature=0.7,top_k=50,max_output_tokens=1000)
        #models/text-bison-001
        # Split the response into paragraphs based on newline characters
        paragraphs = response.result.split('\n')
        
        # Remove empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Add the chatbot's response to the conversation history
        assistant_message_history.extend(paragraphs)
        print(paragraphs)
        
        return paragraphs

    except Exception as e:
        return [str(e)]  # Return an array with the error message as a single paragraph


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get user input and selected chatbot from JSON data
        data = request.get_json()
        user_input = data.get('user_input')
        selected_chatbot = data.get('selected_chatbot')
        
        # Call the appropriate chatbot function based on the selected chatbot
        if selected_chatbot == "chatbot1":
            print("llamav1_selected")
            chatbot_response = llama_chatbot(user_input, conversation_context_1)
        elif selected_chatbot == "chatbot2":
            print("llamav2_selected")
            chatbot_response = llama_chatbot_v2(user_input, conversation_context_2)
        elif selected_chatbot == "chatbot3":  
            print("palm_selected")
            chatbot_response = palm_chatbot(user_input,conversation_context_3)
        else:
            return jsonify({"error": "Invalid chatbot selection"})
        # Return the response as JSON along with updated conversation context
        return jsonify({"response": chatbot_response})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
