

# # Define the response function
# def bot_message(text):
#     st.session_state.messages.append({"role": "assistant", "content": text})
#     with st.chat_message("assistant"):
#         for char in text:
#             yield char
#             time.sleep(0.01)
#     return text
    
    
# def user_message():
#     user_input= st.chat_input("Your response:")
#     st.session_state.messages.append({"role": "user", "content": user_input})
#     return user_input
# # Function to simulate conversation progression
# def next_step():
#     st.session_state.step += 1


# # Initialize session state
# if "step" not in st.session_state:
#     st.session_state.step = 0

# #define conversation steps
# conversation_steps = [
#     {"question":"Which Land cover class", "response":{"Tree cover":2, "Land cover":2, "I have preexisting LC files":3}},
#     {"question":"Do you have preexisting polygon files", "response":{"yes":5, "no":4}},
#     {"question":"Upload LC files", "response":{"file":2}},
#     {"question":"Do you have your own observational data or do you want to source it from Gbif", "response":{"my own":6, "Gbif":7}},
#     {"question":"upload poly file, LC/TC still to be implemented ", "response":{"file":12}},
#     {"question":"Upload obs files", "response":{"file":11}},
#     {"question":"is your area of interest a country or do you want to give a bbox", "response":{"bbox":8, "country":9}},
#     {"question":"Enter bbox", "response":{"bbox":10}},
#     {"question":"Enter country", "response":{"country":10}},
#     {"question":"Enter species name", "response":{"species":11}},
#     {"question":"buffer size", "response":{"buffer":12}},
#     {"question":"LC type", "response":{"LC type":13}}, 
#     {"question":"years of interest", "response":{"2000":"end"}}
#     ]

# st.title("Interactive Response Example")
# step_data=conversation_steps[st.session_state.step]
# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Initialize user input save
# if "save" not in st.session_state:
#     st.session_state.save= []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if not st.session_state.messages:
#     # Bot asks the first question
#     first_message = "Hello! Im an assist bot to fill out the Genes from space tool. How may i help you?"
#     st.write_stream(bot_message(first_message))
#     st.write_stream(bot_message(step_data["question"]))


# if prompt := st.chat_input("Your response:"):
#     #display user prompt
#     st.chat_message("user").markdown(prompt)
#     #add user prompt to memory
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     #save prompt as Input for tool
#     st.session_state.save.append(prompt)
#     #check if prompt is a valid response
#     if step_data["response"][prompt]== "end":
#         st.json(st.session_state.save)
#         exit()   
#     if prompt in step_data["response"]:
#             new_step = step_data["response"][prompt]-1
#             # st.write_stream(bot_message(bot_response))
#             st.session_state.step=new_step
#     else:
#         bot_response = step_data["default"]
#         st.write_stream(bot_message(bot_response))



#     step_data=conversation_steps[st.session_state.step]
#     st.write_stream(bot_message(step_data["question"]))
    





# [{"question":"Which Land cover class", "response":{"Tree cover":2, "Land cover":2, "I have preexisting LC files":3}},
# {"question":"Do you have preexisting polygon files", "response":{"Yes":5, "No":4}},
# {"question":"Upload LC files", "response":{"file":2}},
# {"question":"Do you have your own observational data or do you want to source it from Gbif", "response":{"my own":6, "Gbif":7}},
# {"question":"upload poly file, LC/TC still to be implemented ", "resoponse":{"file":12}}
# {"question":"Upload obs files", "response":{"file":11}},
# {"question":"is your area of interest a country or do you want to give a bbox", "response":{"bbox":8, "country":9}},
# {"question":"Enter bbox", "response":{{}:10}},
# {"question":"Enter bbox", "response":{{}:10}},
# {"question":"Enter species name", "response":{{}:11}}]

import streamlit as st
import time
import pandas as pd
from io import StringIO

# Initialize user input save
if "save" not in st.session_state:
    st.session_state.save= {}

st.write("Hello! This is a automatic fill out form for the Genes from Space Tool. It helps you find the right Pipeline for your needs")
url = "https://pipelines-2.geobon.org/pipeline-form/GenesFromSpace%3EToolComponents%3EGetHabitatMaps%3EGFS_Habitat_map_GFW_tree_canopy_2000-2023"
st.write("If you want to check all the pipelines on your own check this out [link](%s)" % url)

LCtype=""
poly=""
points=""
area_type=""


LCtype= st.selectbox(
    'Select Land cover Type:',
    ('Tree cover', 'Land cover'),
    index=None,
    placeholder="Select LC Type...")

if LCtype:
    st.session_state.save["LCtype"]=LCtype
    poly=st.radio(
        "Do you have preprocessed polygons?",
        key="visibility",
        options=["yes", "no"],
        index=None
    )

if poly=="yes":
    polygon_file = st.file_uploader("Choose a file")
    if polygon_file is not None:
        # To read file as bytes:
        bytes_data = polygon_file.getvalue()

        # To convert to a string based IO:
        stringio = StringIO(polygon_file.getvalue().decode("utf-8"))
        # To read file as string:
        string_data = stringio.read()
        # Can be used wherever a "file-like" object is accepted:
        polygons = pd.read_csv(polygon_file)
        st.write(polygons)
        st.session_state.save["poly"]="NA"
        st.session_state.save["points"]="NA"
        st.session_state.save["area_type"]= "NA"


if poly=="no":
     st.session_state.save["poly"]="no"
     points=st.radio(
        "Do you have preprocessed polygons?",
        options=["GBIF", "preexisting observations"],
        index=None
    )

if points=="preexisting observations":
    obs_file = st.file_uploader("Choose a file")
    if obs_file is not None:
        # To read file as bytes:
        bytes_data = obs_file.getvalue()

        # To convert to a string based IO:
        stringio = StringIO(obs_file.getvalue().decode("utf-8"))
        # To read file as string:
        string_data = stringio.read()
        # Can be used wherever a "file-like" object is accepted:
        obs = pd.read_csv(obs_file)
        st.write(obs)
        st.session_state.save["points"]="pre"
        st.session_state.save["area_type"]= "NA"

if points=="GBIF":
    st.session_state.save["points"]="GBIF"
    area_type=st.radio(
        "Country or BBox?",

        options=["BBox", "Country"],
        index=None
    )
    
if area_type:
            st.session_state.save["area_type"]=area_type


if len(st.session_state.save)==4:
    st.write("Are yo happy with your choices? If so click on Submit and you will be directed to the correct pipeline.")
    if st.button("Commit"):
        st.write(st.session_state.save)




