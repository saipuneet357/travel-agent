import streamlit as st
import requests
import json
import time
import sys
import os

# Get the directory of the current file (child/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (project_root/) to sys.path
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from redis_db import RedisClient


st.set_page_config(page_title="Awara Chat", page_icon=":tada:", layout="wide"
)
redis_client = RedisClient(host='localhost', port=6379, db=0)

# API endpoint - replace with your actual endpoint later
API_ENDPOINT = "http://localhost:11434/api/chat"

st.title("Awara Chat")

# Text input
user_input = getattr(st.chat_input("Chat with Awara:", accept_file=True,
    file_type=["jpg", "jpeg", "png"],), 'text', None)

# When Enter is pressed or button is clicked
if user_input:
    
    # First, search the llmcache using RediSearch
    try:
        # Search for existing responses
        search_results = redis_client.search_prompt(user_input, distance_threshold=0.4)
        is_a_match = next(search_results)

        if is_a_match:
            # Found in cache - stream the cached response
            st.success("Cache Hit - Streaming Cached Response")
            cached_response = search_results
            
            # Create a placeholder for the text area
            text_placeholder = st.empty()
            
            # Stream the cached response character by character for visual effect
            response_text = ""
            for char in cached_response:
                response_text += char
                text_placeholder.text_area(
                    "Response:",
                    value=response_text,
                    height='content',
                    disabled=False,
                    key=f"cached_response_{len(response_text)}"
                )
                time.sleep(0.005)

        else:
            # Not found in cache - hit the LLM endpoint
            st.info("Cache Miss - Querying LLM")
            
            data = {
                "model": "awara",
                "messages": [
                    {"role": "user", "content": f"{user_input}"}
                ]
            }
            response = requests.post(
                API_ENDPOINT,
                json=data,
                stream=True
            )
            
            # Display streaming response
            if response.status_code == 200:
                st.success("Streaming Response")
                # Create a placeholder for the text area that will update in real-time
                text_placeholder = st.empty()
                # Accumulate streaming response content
                response_text = ""
                
                # Stream the response and update the text area in real-time
                i = 0
                delimiter_seen = False
                metadata = ''
                collecting_metadata = False
                delimiter_started = False
                
                for line in response.iter_lines(decode_unicode=True):
                    i += 1
                    if line:
                        try:
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                content = data['message']['content']
                                
                                # Check if we've hit the first delimiter
                                if not delimiter_seen:
                                    if "---" in content:
                                        delimiter_seen = True
                                        delimiter_started = True
                                        # print(content)
                                       
                                    else:
                                        # Normal content accumulation before delimiter
                                        response_text += content
                                        # Update the text area with accumulated content in real-time
                                        text_placeholder.text_area(
                                            "Response:",
                                            value=response_text,
                                            height='content',
                                            disabled=False,
                                            key=f"streaming_response_{i}"
                                        )
                                elif collecting_metadata:
                                    # We're collecting metadata between delimiters
                                    metadata += content

                                elif delimiter_started:
                                    # We're collecting metadata between delimiters
                                    if "---" in content:
                                        collecting_metadata = True
                                        
                                    else:
                                        continue
                                        

                        except json.JSONDecodeError:
                            st.warning(f'Failed to parse: {line}')
                
                # Store the response in semantic cache asynchronously in the background
                if response_text:
                    print('Inserting response into Redis')
                    prompt_id = redis_client.insert_prompts([{'prompt': user_input, 'response': response_text}])
                    clean = json.loads(metadata.replace("\n", "").replace('*', '').strip())
                    clean['user_id'] = st.session_state['user_id']
                    clean['prompt_id'] = prompt_id
                    print(clean)
            
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
