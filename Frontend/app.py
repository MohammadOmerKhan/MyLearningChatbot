import gradio as gr
import requests
import json

current_session_id = None


def chat_with_ai(message, history):
    global current_session_id

    try:
        response = requests.post(
            "http://localhost:8000/chat/send",
            json={"message": message, "session_id": current_session_id},
        )

        if response.status_code == 200:
            data = response.json()
            current_session_id = data["session_id"]
            history.append(
                [message, data["response"]]
            )  # return the updated chat history

            return history
        else:
            history.append([message, "Unable to connect to AI service."])
            return history
    except Exception as e:
        history.append([message, f"Error: {str(e)}"])
        return history


def save_document_to_db(file):
    if file is None:
        return "No file selected"

    try:
        files = {"file": open(file.name, "rb")}
        response = requests.post("http://localhost:8000/documents/upload", files=files)
        if response.status_code == 200:
            result = response.json()
            return f" {result['message']}"
        else:
            return "Failed to save document"
    except Exception as e:
        return f"Error: {str(e)}"


with gr.Blocks() as demo:
    gr.Markdown("# Netsol Chatbot")
    gr.Markdown("Chatbot Made By Omer khan")

    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Type a message...")
            submit_btn = gr.Button("Submit")

        with gr.Column():
            file_input = gr.File(label="Upload Document", file_types=[".pdf", ".txt"])
            save_btn = gr.Button("Save to Database", variant="secondary")
            save_status = gr.Textbox(label="Save Status", interactive=False)

    save_btn.click(
        fn=save_document_to_db, inputs=[file_input], outputs=[save_status]
    )  # save to database function called

    submit_btn.click(
        fn=chat_with_ai,
        inputs=[msg, chatbot],
        outputs=[chatbot],  # chat function called
    )


if __name__ == "__main__":
    demo.launch(debug=True)
