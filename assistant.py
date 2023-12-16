import os
import time
import streamlit as st
import json

from openai import OpenAI

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    
client = OpenAI()

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def pretty_print(messages):
    responses = []
    for m in messages:
        if m.role == "assistant":
            responses.append(m.content[0].text.value)
    return "\n".join(responses)


def main():

    assistant = client.beta.assistants.create(
    name = "Nutritionist",
    instructions = "You are a helpful nutritional expert. You focus on calorie intake and give people advice on healthy food options and the nutrional value of those options.",
    tools = [{"type":"code_interpreter"}, {"type": "retrieval"}],
    model = "gpt-4-1106-preview"
    )
    
    thread = client.beta.threads.create()
    
    assistant_option = st.sidebar.selectbox(
        "Select an Assistant",
        ("Nutritionist", "Advisor")
    )
    
    if assistant_option == "Nutritionist":
        st.title("Nutritionist :bar_chart:")
        
        # Description
        st.markdown("""
            This assistant is your go-to resource for nutrition insights and advice. Here's what you can do:
            
            Simply enter your query below and let the assistant guide you with actionable insights.
        """)
        
        user_query = st.text_input("Enter your query:")
        
        if st.button('Get Insight') and client:
            with st.spinner('Fetching...'):
                thread = client.beta.threads.create()
                run = submit_message(assistant.id, thread, user_query)
                run = wait_on_run(run, thread)
                response_messages = get_response(thread)
                response = pretty_print(response_messages)
                st.text_area("Response:", value=response, height=300)

if __name__ == "__main__":
    main()

