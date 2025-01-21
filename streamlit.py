import streamlit as st
from test_legal_opensearch import main2
import json
import sys
from io import StringIO
import json
import textwrap
from tabulate import tabulate

st.set_page_config(layout="wide")

# Custom CSS to increase the width of the main content area
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 95%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 95%;
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
    }
    .stChatMessage {
        width: 100%;
    }
    .stChatInput {
        width: 100%;
    }
    .stMarkdown {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


st.title("Legal Doc. Inspector")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to call API
def call_api(prompt):
    output= main2(prompt)
    print("vineet")
    response = output['hits']['hits']
    print (response)
    print("vineete")
    return response


st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 95%;
    }
    .stTable {
        width: 100%;
    }
    .stTable td {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

def format_response(response):
    formatted_output = f"Total number of results: {len(response)}\n\n"
    
    for item in response:
        source = item['_source']
        formatted_output += f"### Company: {source['company']}\n\n"
        
        table_data = [
            ["Field", "Value"],
            ["Source URI", source['x-amz-bedrock-kb-source-uri']],
            # ["Time Entry Requirements", source['time_entry_requirements']],
            ["Agreement Date", source['Agreement_date']],
            # ["Types of Expenses", source['types_of_expenses']],
            ["Breach Notification Required", source['breach_notification_required']]
         
        ]
        
        formatted_output += tabulate(table_data, headers="firstrow", tablefmt="pipe") + "\n\n"
        
        formatted_output += "**Document Passage:**\n\n"
        
        wrapped_text = textwrap.fill(source['AMAZON_BEDROCK_TEXT'], width=100)
        formatted_output += f"{wrapped_text}\n\n"
        formatted_output += "---\n\n"
    
    return formatted_output





# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Call API and get response
    api_response = call_api(prompt)
    
    # Format and display API response
    formatted_response = format_response(api_response)
    with st.chat_message("assistant"):
        st.markdown(formatted_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
