import streamlit as st
import requests
import os

# Page config
st.set_page_config(
    page_title="AI PDF Chat",
    page_icon="📄",
    layout="wide"
)

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def main():
    st.title("📄 AI PDF Chat")
    st.markdown("*Stop reading, start asking*")

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Maximum 10MB"
        )

        if uploaded_file:
            process_pdf(uploaded_file)

    # Main chat interface
    if 'pdf_id' in st.session_state:
        chat_interface()
    else:
        show_welcome()

def show_welcome():
    st.markdown("""
    ### ✨ Features
    - 🎯 Accurate answers with source citations
    - ⚡ 2 hours reading → 10 minutes understanding
    - 🆓 Free to try, no registration needed

    👈 Upload a PDF to get started!
    """)

def process_pdf(file):
    with st.spinner("Processing PDF..."):
        try:
            # Upload to backend
            files = {"file": (file.name, file, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)

            if response.status_code == 200:
                data = response.json()
                st.session_state['pdf_id'] = data['pdf_id']
                st.session_state['filename'] = data['filename']
                st.session_state['page_count'] = data['page_count']
                st.session_state['messages'] = []
                st.success(f"✅ Processed {data['filename']} ({data['page_count']} pages)")
                st.rerun()
            else:
                st.error(f"Failed to process PDF: {response.text}")
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")

def chat_interface():
    # Display PDF info
    st.info(f"📄 {st.session_state['filename']} ({st.session_state['page_count']} pages)")

    # Show suggested questions if no messages yet
    if len(st.session_state.messages) == 0:
        st.markdown("### 💡 Suggested Questions")

        # Get suggestions from backend
        suggestions = get_suggestions()

        cols = st.columns(len(suggestions))
        for idx, q in enumerate(suggestions):
            with cols[idx]:
                if st.button(q, key=f"suggest_{idx}", use_container_width=True):
                    # Add the question and trigger answer
                    ask_question_internal(q)

    # Chat history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            if 'sources' in msg and msg['sources']:
                with st.expander("📍 View sources"):
                    for source in msg['sources']:
                        st.caption(f"**Page {source['page']}**: {source['text'][:200]}...")

    # Input
    if question := st.chat_input("Ask a question about the PDF"):
        ask_question_internal(question)

def ask_question_internal(question: str):
    """Internal function to handle question asking"""
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': question
    })

    # Display user message
    with st.chat_message('user'):
        st.markdown(question)

    # Get answer
    with st.chat_message('assistant'):
        with st.spinner("Thinking..."):
            answer_data = get_answer(question)
            st.markdown(answer_data['answer'])

            # Show sources
            if answer_data.get('sources'):
                with st.expander("📍 View sources"):
                    for source in answer_data['sources']:
                        st.caption(f"**Page {source['page']}**: {source['text'][:200]}...")

            # Add feedback buttons
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"like_{len(st.session_state.messages)}"):
                    send_feedback(question, answer_data['answer'], 'helpful')
                    st.success("Thanks!")
            with col2:
                if st.button("👎", key=f"dislike_{len(st.session_state.messages)}"):
                    send_feedback(question, answer_data['answer'], 'inaccurate')
                    st.warning("Feedback recorded")

    # Add assistant message
    st.session_state.messages.append({
        'role': 'assistant',
        'content': answer_data['answer'],
        'sources': answer_data.get('sources', [])
    })

    # Rerun to update the UI
    st.rerun()

def get_answer(question: str):
    """Get answer from backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                'pdf_id': st.session_state['pdf_id'],
                'question': question
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                'answer': f'❌ Failed to get answer: {response.text}',
                'sources': []
            }
    except Exception as e:
        return {
            'answer': f'❌ Error: {str(e)}',
            'sources': []
        }


def send_feedback(question: str, answer: str, feedback_type: str):
    """发送用户反馈到后端"""
    try:
        requests.post(
            f"{BACKEND_URL}/feedback",
            json={
                'pdf_id': st.session_state['pdf_id'],
                'question': question,
                'answer': answer,
                'feedback': feedback_type
            },
            timeout=5
        )
    except Exception as e:
        print(f"Failed to send feedback: {str(e)}")


if __name__ == "__main__":
    main()
