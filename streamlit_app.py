import streamlit as st
import requests

st.title("📰 Smart Company News Chatbot")

message = st.text_input("Ask about company news or say hi!")

if 'chat' not in st.session_state:
    st.session_state['chat'] = []

if st.button("Send") and message.strip():
    st.session_state.chat.append({"user": message})

    url = "http://localhost:5005/webhooks/rest/webhook"
    res = requests.post(url, json={"sender": "user", "message": message})
    if res.ok:
        for botmsg in res.json():
            if botmsg.get("text"):
                st.session_state.chat.append({"bot": botmsg["text"]})

for entry in st.session_state.chat:
    if 'user' in entry:
        st.markdown(f"**You:** {entry['user']}")
    if 'bot' in entry:
        st.markdown(f"**Bot:** {entry['bot']}")
