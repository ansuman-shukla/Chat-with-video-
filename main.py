import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract transcript from a YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_text])
        return transcript.strip()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Generation configuration for Google Generative AI
generation_config = {
    "temperature": 0.1,
    "top_p": 0.5,
    "top_k": 16,
    "max_output_tokens": 20000,
}

# Function to generate a response from the AI model
def generate_response(chat_session, prompt):
    response = chat_session.send_message(prompt)
    return response.text

# Initialize Streamlit app
st.title("Chat With Video 🤖")

# Initialize session state for chat session and chat history
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# YouTube video URL input
youtube_link = st.text_input("Enter YouTube Video URL:")

# Only run transcript extraction once
if st.button("Analyze"):
    if youtube_link:
        with st.spinner("Extracting and analyzing transcript..."):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                # Initial setup for chat session
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro-exp-0827",
                    generation_config=generation_config,
                )
                
                # Store the transcript and initial prompt in session state
                st.session_state.transcript = transcript_text
                st.session_state.chat_session = model.start_chat(history=[])
                
                # Create initial prompt with transcript
                initial_prompt= f"""You are an expert BOOK INDEXER tasked with organizing the transcript of a YouTube video. Your goal is to  arrange the information in a structured, markdown-formatted outline. Follow these strict guidelines and KEEP your response in English:

                    # 1. Use proper markdown syntax for formatting.
                    # 2. Each TOPIC should be a level 2 heading (##) and in bold.
                    # 3. Each SUB-TOPIC should be a level 3 heading (###).
                    # 4. Each Description should be a Bullet points.
                    # 5. [Conclusion] should have all the TOPIC in Oderd List.
                    # 7. Use line breaks appropriately for clear separation of sections.
                    # 8. For one prompt choose one out of [summary_format, quiz_format].

                    summary_format:
                    Structure your response as follows:

                    ## **1. [Main Topic 1 ]**

                     ### 1.1 [Sub-Topic 1.1  :- Description] 

                     ### 1.2 [Sub-Topic 1.2  :- Description]

                     ## **2. [Main Topic 2 ]**

                    ### 2.1 [Sub-Topic 2.1  :- Description]

                    ### 2.2 [Sub-Topic 2.2  :- Description]

                    [Continue this pattern for all main topics and sub-topics covered in the video]
                    # If explictally requested multiple-choice quiz,Follow these strict guidelines:
                    quiz_format:
                    # 1. Each [Question] should be in bold.
                    # 2. Each [Option] should be a Oderd List.
                    # 3. Use line breaks appropriately for clear separation of [Question] and [Option].

                Transcript: {transcript_text}
                """

                # Generate the initial response
                initial_response = generate_response(st.session_state.chat_session, initial_prompt)
                
                # Store initial response in chat history
                st.session_state.chat_history.append(("assistant", initial_response))
                st.rerun()
            else:
                st.error("Failed to extract transcript.")
    else:
        st.warning("Please enter a YouTube video URL.")

# Chat interaction
if st.session_state.chat_session:
    st.subheader("Chat:")
    for role, text in st.session_state.chat_history:
        if role == "human":
            st.markdown(f"""
            <div style="background-color: #808080; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                <strong>😄 You:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(text)

    # Form to handle user input
    with st.form(key='chat_form'):
        user_input = st.text_input("Ask a question about the video:", key="user_input")
        submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            # Store user question in chat history
            st.session_state.chat_history.append(("human", user_input))
            
            # Generate a response based on user input, using the existing chat session
            response = generate_response(st.session_state.chat_session, user_input)
            
            # Append the AI's response to the chat history
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()





# import os
# import streamlit as st
# from dotenv import load_dotenv
# import google.generativeai as genai
# from youtube_transcript_api import YouTubeTranscriptApi

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def extract_transcript_details(youtube_video_url):
#     try:
#         video_id = youtube_video_url.split("=")[1]
#         transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
#         transcript = ""
#         for i in transcript_text:
#             transcript += i["text"] + " "
#         return transcript.strip()
#     except Exception as e:
#         st.error(f"An error occurred: {str(e)}")
#         return None

# generation_config = {
#     "temperature": 0.1,
#     "top_p": 0.5,
#     "top_k": 16,
#     "max_output_tokens": 20000,
#     # "response_mime_type": "application/json",
# }

# def generate_response(model, prompt):
#     response = model.send_message(prompt)
#     return response.text


# prompt = """You are an expert BOOK INDEXER tasked with organizing the transcript of a YouTube video. Your goal is to arrange the information in a structured, markdown-formatted outline. Follow these strict guidelines:

# 0. Always give TOPIC & SUB-TOPIC from transcript till [Conclusion].
# 1. Use proper markdown syntax for formatting.
# 2. Each TOPIC should be a level 2 heading (##) and in bold.
# 3. Each SUB-TOPIC should be a level 3 heading (###).
# 4. Each Description should be a Bullet points.
# 5. Use line breaks appropriately for clear separation of sections.
# 6. For this prompt choose only one out of [summary_format, quiz_format , True/False Questions , Logical Reasoning Questions] if one is choosen another can't be choosen.


# summary_format:
# Structure your response as follows:

# ## **1. [Main Topic 1 ]**

# ### 1.1 [Sub-Topic 1.1  :- Description] 

# ### 1.2 [Sub-Topic 1.2  :- Description]

# ## **2. [Main Topic 2 ]**

# ### 2.1 [Sub-Topic 2.1  :- Description]

# ### 2.2 [Sub-Topic 2.2  :- Description]

# [Continue this pattern for all main topics and sub-topics covered in the video]

# ////------------////

# If specifically requested, you can provide a brief multiple-choice quiz section to reinforce key concepts,Follow these strict guidelines:

# 1. Each [Question] should be a level 2 heading (##) and in bold.
# 2. Each [Option] should be a Bullet points.
# 3. Use line breaks appropriately for clear separation of sections.

# quiz_format:
# ## Quiz
# 1. [Question]
#    a) [Option 1]
#    b) [Option 2]
#    c) [Option 3]
#    d) [Option 4]
# [Continue pattern for additional MCQ questions]

# ////------------////
   
# If the quiz includes True/False questions,Follow these strict guidelines:

# 1. Each [True/False Question] should be a level 2 heading (##) and in bold.
# 2. The [Answer Options] should be simple bullet points with 'True' and 'False'.
# 3. Use line breaks appropriately for clear separation of questions.

# True/False Questions:
# Structure your response as follows:

# ## True/False Quiz

# ### 1. [True/False Question]
#    - True
#    - False

# [Continue pattern for additional True/False questions]

# ////------------////

# If the quiz includes Logical Reasoning questions,Follow these strict guidelines:

# 1. Each [Logical Reasoning Question] should be a level 2 heading (##) and in bold.
# 2. The answer to each logical reasoning question should be one comprehensive, detailed response, in paragraph form.
# 3. Use line breaks appropriately for clear separation of questions and answers.


# Logical Reasoning Questions:
# ## Logical Reasoning Quiz

# ### 1. [Logical Reasoning Question]
#    - [Write a detailed, single-paragraph answer for this question.]

# [Continue pattern for additional Logical Reasoning questions]

# ////------------////
# """

# st.title("Chat With Video 🤖")

# if 'chat_session' not in st.session_state:
#     st.session_state.chat_session = None

# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []

# youtube_link = st.text_input("Enter YouTube Video URL:")

# if st.button("Analyze"):
#     if youtube_link:
#         with st.spinner("Extracting and analyzing transcript..."):
#             transcript_text = extract_transcript_details(youtube_link)
#             if transcript_text:
#                 model = genai.GenerativeModel(
#                     model_name="gemini-1.5-pro-exp-0827",
#                     generation_config=generation_config,
#                 )
#                 st.session_state.chat_session = model.start_chat(history=[])
#                 initial_response = generate_response(st.session_state.chat_session, prompt + transcript_text)
#                 print(initial_response)
#                 st.session_state.chat_history.append(("assistant", initial_response))
#                 st.rerun()
#             else:
#                 st.error("Failed to extract transcript.")
#     else:
#         st.warning("Please enter a YouTube video URL.")

# if st.session_state.chat_session:
#     st.subheader("Chat:")
#     for role, text in st.session_state.chat_history:
#         if role == "human":
#             st.markdown(f"""
#             <div style="background-color: #808080 ; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
#                 <strong>😄 You:</strong> {text}
#             </div>
#             """, unsafe_allow_html=True)
#         else:
#             st.markdown(text)

#     # Use a form to handle the Enter key press
#     with st.form(key='chat_form'):
#         user_input = st.text_input("Ask a question about the video:", key="user_input")
#         submit_button = st.form_submit_button("Send")

#         if submit_button and user_input:
#             st.session_state.chat_history.append(("human", user_input))
#             response = generate_response(st.session_state.chat_session, user_input)
#             st.session_state.chat_history.append(("assistant", response))
#             st.rerun()