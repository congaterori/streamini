import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import tempfile


def is_arabic(text):
    """Checks if the text contains any Arabic characters."""
    return any(char in text for char in set("ابتثجحخدذرزسشصضطظعغفقكلمنهوي"))

def create_model(model_name, system_prompt):
    """Creates and configures a GenerativeModel instance."""
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.45,
        "top_k": 25,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Use system instruction only for specific models
    system_instruction = (
        system_prompt
        if model_name
        in [
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro-exp-0827",
            "gemini-1.5-flash-exp-0827",
        ]
        else None
    )

    # Safety settings (currently set to block none)
    safety_settings = {
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    }

    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction=system_instruction,
    )

def display_chat_message(role, message):
    """Displays a chat message with appropriate formatting."""
    if role == "user":
        if "image" in message:
            st.chat_message("user").image(
                message["image"], caption=message.get("caption", "")
            )
        if "content" in message:
            st.chat_message("user").markdown(message["content"], unsafe_allow_html=True)
    else:
        if "content" in message:
            if is_arabic(message["content"]):
                st.chat_message("assistant").markdown(
                    f'<div dir="rtl">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.chat_message("assistant").markdown(
                    message["content"], unsafe_allow_html=True
                )

def handle_text_message(user_message, chat_session):
    """Handles user text messages and generates responses."""
    try:
        message_data = {"role": "user", "content": user_message}
        st.session_state.messages.append(message_data)
        st.chat_message("user").markdown(user_message, unsafe_allow_html=True)

        response = chat_session.send_message(user_message)
        response_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        display_chat_message("assistant", {"content": response_text})

    except Exception as e:
        st.error(f"An error occurred: {e}")

def handle_image_upload(uploaded_image, image_comment, chat_session):
    """Handles image uploads and generates responses."""
    if uploaded_image:
        if not image_comment.strip():
            st.error("Please add a comment before sending the image.")
        else:
            try:
                image = Image.open(uploaded_image)
                message_data = {"role": "user", "image": image, "caption": image_comment}

                st.session_state.messages.append(message_data)
                st.chat_message("user").image(image, caption=image_comment)

                response = chat_session.send_message([image_comment, image])
                response_text = response.text

                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )

                display_chat_message("assistant", {"content": response_text})

            except Exception as e:
                st.error(f"An error occurred: {e}")

def handle_document_upload(uploaded_document, document_comment, chat_session):
    """Handles document uploads and generates responses."""
    if uploaded_document:
        if not document_comment.strip():
            st.error("Please add a comment before sending the document.")
        else:
            try:
                # Handle PDF files using the File API
                if uploaded_document.type == "application/pdf":
                    pdf_file_name = uploaded_document.name
                    # Save the uploaded PDF to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                        temp_pdf.write(uploaded_document.read())
                        temp_pdf_path = temp_pdf.name

                    # Upload the temporary PDF file using its path
                    pdf_file = genai.upload_file(
                        path=temp_pdf_path,
                        display_name=uploaded_document.name
                    )


                    # Display PDF in chat
                    # with open(temp_pdf_path, "rb") as f:
                        # base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="560" height="800" type="application/pdf"></iframe>'

                    pdf_chat_message = f"""
                                        **{pdf_file_name}**\n```\n{document_comment}\n```\n
                                        """

                    message_data = {"role": "user", "content": pdf_chat_message, "caption": document_comment, "file_name": pdf_file_name}
                    st.session_state.messages.append(message_data)
                    st.chat_message("user").markdown(pdf_chat_message, unsafe_allow_html=True)

                    # Remove the temporary file after uploading
                    os.remove(temp_pdf_path)
                    
                    # Send the PDF URI and comment to the model
                    response = st.session_state.chat_session.send_message([document_comment, pdf_file])
                    
                else:  # Handle text-based files
                    document_content = uploaded_document.read().decode("utf-8")

                    document_chat_message = f"""
                                            ## {document_comment}:\n---\n```\n{document_content}\n```\n---
                                            """

                    message_data = {
                        "role": "user",
                        "content": document_chat_message,
                        "caption": document_comment,
                    }
                    st.session_state.messages.append(message_data)

                    st.chat_message("user").markdown(
                        document_chat_message, unsafe_allow_html=True
                    )

                    # Send the text content and comment to the model
                    response = chat_session.send_message(
                        [document_comment, document_content]
                    )

                response_text = response.text
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )

                display_chat_message("assistant", {"content": response_text})

            except Exception as e:
                st.error(f"An error occurred: {e}")
