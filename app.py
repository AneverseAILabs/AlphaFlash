import streamlit as st

st.title("🧠 Simple Streamlit Test App")

name = st.text_input("Enter your name:")

if st.button("Greet Me"):
    st.success(f"Hello, {name or 'there'}! 👋 Welcome to your first Streamlit app.")

st.write("---")
st.write("✅ This is a simple app running without any external API.")
st.write("You can later integrate OpenAI or other APIs easily.")
