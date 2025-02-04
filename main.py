from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
import asyncio
import streamlit as st


# Set up page config
st.set_page_config(
    page_title="Learn with AI",
    page_icon="🤖",
    layout="centered"
)

# Initialize chat histories
if "histories" not in st.session_state:
    st.session_state.histories = {
        "Tim": [],
        "Nina": [],
        "Jake": []
    }

# Track current character
if "current_character" not in st.session_state:
    st.session_state.current_character = "Tim"



CHARACTER_PROMPTS = {
    "Tim": (
        "You're Tim, a curious 5-year-old boy. Speak simply with occasional grammar mistakes. "
        "When someone explains something new, ask ONE child-like question about it. "
        "For normal chat, respond like an excited kid. Examples:\n"
        "- Topic: 'Plants eat sunlight' → 'Why plants hungry for light?'\n"
        "- Greeting: 'Hi Tim!' /→ 'Hello am very interested in learning something from you.'"
    ),
    "Nina": (
        "You're Nina, a curious adult with broad general knowledge. Ask thoughtful but accessible follow-up questions. "
        "Focus on practical applications and common misunderstandings. "
        "Keep questions grounded in everyday experience. Examples:\n"
        "- Topic: 'Quantum entanglement' → 'How could this affect normal computer technology?'\n"
        "- Topic: 'Climate change' → 'Would this explain why winters feel warmer now?'\n"
        "- Greeting: 'Hello' → 'Hi! I'm curious about something - can you explain it to me?'"
    ),
    "Jake": (
        "You're Jake, an enigmatic polymath. Use sophisticated language with dry wit. "
        "When receiving explanations, challenge with ONE paradoxical question. "
        "Keep casual chat intriguingly brief. Examples:\n"
        "- Topic: 'AI ethics' → 'Can moral frameworks exist without anthropocentric bias?'\n"
        "- Greeting: 'Hey Jake' → 'Proceed. I'm listening.'"
    )
}






def get_groq_response(prompt, character):
    try:
        groq_api_key=st.secrets["api_key"]
        model = GroqModel('llama-3.3-70b-versatile',api_key=groq_api_key)

        agent = Agent(
            model,  
            system_prompt=CHARACTER_PROMPTS[character],  
        )
        ans = agent.run_sync(prompt).data
        return ans
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# App UI
st.title("🤖 Teach Your AI Student")
st.caption("Choose a learner personality from the sidebar and explain any concept!")

# Sidebar with character selection
with st.sidebar:
    st.header("Student Profile")
    new_character = st.radio(
        "Select your student:",
        ["Tim", "Nina", "Jake"],
        index=0,
        key="character_selector",
        label_visibility="collapsed"
    )
    
    # Update current character if changed
    if new_character != st.session_state.current_character:
        st.session_state.current_character = new_character
        st.rerun()
    
    # Character descriptions
    st.divider()
    st.subheader("Current Learner:")
    if new_character == "Tim":
        st.markdown("🧒 **Tim**  \nCurious 5-year-old with simple questions.")
    elif new_character == "Nina":
        st.markdown("👩💻 **Nina**  \nPractical thinker making real-world connections with challenging questions.")
    else:
        st.markdown("🧞♂️ **Jake**  \nChallenging knowledge architect with complex questions.")

# Display current character's chat history
avatar_mapping = {
    "user": "🧑",
    "Tim": "🧒",
    "Nina": "👩",
    "Jake": "🧞"
}

current_history = st.session_state.histories[st.session_state.current_character]

for message in current_history:
    role = message["role"]
    avatar = avatar_mapping[role] if role == "user" else avatar_mapping[st.session_state.current_character]
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Handle new input
if prompt := st.chat_input(f"Explain something to {st.session_state.current_character}..."):
    if not st.secrets["api_key"]:
        st.error("Missing Groq API key! Set in secrets.toml file.")
        st.stop()
    
    # Add user message to current character's history
    current_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Generate and display response
    with st.spinner(f"{st.session_state.current_character} is thinking..."):
        response = get_groq_response(prompt, st.session_state.current_character)
    
    if response:
        # Add assistant response to current character's history
        current_history.append({"role": "assistant", "content": response})
        # Display assistant response
        with st.chat_message("assistant", avatar=avatar_mapping[st.session_state.current_character]):
            st.markdown(response)
    else:
        st.error("Failed to generate response")