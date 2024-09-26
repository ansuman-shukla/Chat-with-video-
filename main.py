import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

import re

# Use a single API key
# api_key = st.secrets["google"]["api_key"]

# genai.configure(api_key=api_key)
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# Function to extract video ID from various YouTube URL formats
def get_video_id(youtube_video_url):
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_video_url)
        if match:
            return match.group(1)
    return None

# Function to extract transcript from a YouTube video in all available languages
def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English transcript first
        try:
            transcript = transcript_list.find_transcript(['en'])
            transcript_text = " ".join([item["text"] for item in transcript.fetch()])
            return {"en": transcript_text.strip()}
        except:
            # If English is not available, get the first available transcript
            for transcript in transcript_list:
                try:
                    transcript_text = " ".join([item["text"] for item in transcript.fetch()])
                    return {transcript.language_code: transcript_text.strip()}
                except:
                    continue
            raise Exception("No transcript could be fetched for any language")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Generation configuration for Google Generative AI
generation_config = {
    "temperature": 0.1,
    "top_p": 0.5,
    "top_k": 6,
    "max_output_tokens": 20000,
}

# Function to generate a response from the AI model
def generate_response(chat_session, prompt):
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Initialize Streamlit app
st.set_page_config(page_title="Chat With Video 🤖", page_icon=":movie_camera:")
st.title("Chat With Video 🤖")

# Initialize session state for chat session and chat history
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'role_history' not in st.session_state:
    st.session_state.role_history = []

# YouTube video URL input
youtube_link = st.text_input("Enter YouTube Video URL:")

# Only run transcript extraction once
if st.button("Analyze"):
    if youtube_link:
        with st.spinner("Extracting and analyzing transcript..."):
            transcript_dict = extract_transcript_details(youtube_link)
            if transcript_dict:
                try:
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-pro-exp-0827",
                        generation_config=generation_config,
                    )
                    st.session_state.transcript = transcript_dict
                    st.session_state.chat_session = model.start_chat(history=[])

                    language, transcript_text = next(iter(transcript_dict.items()))

                    initial_prompt = f"""You are an expert BOOK INDEXER tasked with organizing the transcript of a YouTube video. The transcript is in {language} language. Your goal is to arrange the information in a structured, markdown-formatted outline. Follow these strict guidelines and KEEP your response in English:

                        # 1. Use proper markdown syntax for formatting.
                        # 2. Each TOPIC should be a level 2 heading (##) and in bold.
                        # 3. Each SUB-TOPIC should be a level 3 heading (###).
                        # 4. Each Description should be a Bullet points.
                        # 5. [Conclusion] should have all the TOPIC in Ordered List.
                        # 6. Use line breaks appropriately for clear separation of sections.
                        # 7. For one prompt choose one out of [summary_format, quiz_format].

                        summary_format:
                        Structure your response as follows:

                        ## **1. [Main Topic 1 ]**

                         ### 1.1 [Sub-Topic 1.1  :- Description] 

                         ### 1.2 [Sub-Topic 1.2  :- Description]

                         ## **2. [Main Topic 2 ]**

                        ### 2.1 [Sub-Topic 2.1  :- Description]

                        ### 2.2 [Sub-Topic 2.2  :- Description]

                        [Continue this pattern for all main topics and sub-topics covered in the video]
                        
                        # If explicitly requested multiple-choice quiz, follow these strict guidelines:
                        quiz_format:
                        # 1. Each [Question] should be in bold.
                        # 2. Each [Option] should be an Ordered List.
                        # 3. Use line breaks appropriately for clear separation of [Question] and [Option].

                    Transcript:
                    {transcript_text}
                    """

                    initial_response = generate_response(st.session_state.chat_session, initial_prompt)

                    if initial_response:
                        st.session_state.chat_history.append(initial_response)
                        st.session_state.role_history.append("assistant")
                        st.success("Analysis complete! You can now start chatting.")
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
            else:
                st.error("Failed to extract transcript.")
    else:
        st.warning("Please enter a YouTube video URL.")

# Chat interaction
if st.session_state.chat_session:
    st.subheader("Chat:")

    # Display chat history
    for role, text in zip(st.session_state.role_history, st.session_state.chat_history):
        with st.chat_message(role):
            st.markdown(text)

    # User input in the chat
    if prompt := st.chat_input("Your question"):
        st.session_state.chat_history.append(prompt)
        st.session_state.role_history.append("user")
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            response = generate_response(st.session_state.chat_session, prompt)
        
        if response:
            st.session_state.chat_history.append(response)
            st.session_state.role_history.append("assistant")
            with st.chat_message("assistant"):
                st.markdown(response)

# Clear chat button
# Clear chat button
# Clear chat button
st.write("---")
if st.button("Clear Chat"):
    st.session_state.clear()  # This clears all session state variables
    st.success("Chat history cleared! You can start a new conversation.")
