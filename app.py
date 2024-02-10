import streamlit as st
import time
from openai import OpenAI
from PIL import Image

# Display an image
image = Image.open('coco.png')  # Ensure 'coco.png' is the correct path
st.image(image, width=200)  # Adjust width as needed

# Set your OpenAI API key and assistant ID here
api_key = st.secrets["openai_apikey"]
assistant_id = st.secrets["assistant_id"]

# Set OpenAI client, assistant ai and assistant ai thread
@st.cache_resource
def load_openai_client_and_assistant():
    client = OpenAI(api_key=api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()
    return client, my_assistant, thread

client, my_assistant, assistant_thread = load_openai_client_and_assistant()

# Check in loop if assistant ai parses our request
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)
    return run

# Initiate assistant ai response
def get_assistant_response(user_input=""):
    message = client.beta.threads.messages.create(thread_id=assistant_thread.id, role="user", content=user_input)
    run = client.beta.threads.runs.create(thread_id=assistant_thread.id, assistant_id=assistant_id)
    run = wait_on_run(run, assistant_thread)
    messages = client.beta.threads.messages.list(thread_id=assistant_thread.id, order="asc", after=message.id)
    return messages.data[0].content[0].text.value

if 'verified' not in st.session_state:
    st.session_state.verified = False
if 'query' not in st.session_state:
    st.session_state.query = ''
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0  # 初始化消息计数器

def submit():
    user_input = st.session_state.query
    if user_input:  # 检查输入是否非空
        result = get_assistant_response(user_input)
        st.session_state.messages.append(f"👦你：{user_input}")
        st.session_state.messages.append(f"🤖倩仪：{result}")
        st.session_state.query = ''  # 清空输入框
if 'messages' not in st.session_state:
    st.session_state.messages = []
st.title("hi，我是倩仪！")

# User verification input
if not st.session_state.verified:
    with st.form(key='my_form'):
        user_input = st.text_input("输入我的名字开始对话", key="user_input")
        submit_button = st.form_submit_button(label='提交')
        reset_button = False  # Define reset_button outside the if block

        if submit_button:
            if user_input != "赵倩仪":
                st.error("既然我们不认识，我不太有兴趣跟你聊天。")
                reset_button = st.form_submit_button(label='点击这里重置')
            else:
                st.session_state.verified = True
                st.session_user_input = ""
                st.session_state.query = ''
                

        if reset_button:
            st.session_state.verified = False
            st.session_state.user_input = ""

# Chat input and messages display
if st.session_state.verified:
    # 检查对话次数是否已达上限
    if st.session_state.message_count < 50:
        # 注意这里使用 on_change 调用 submit 函数
        st.text_input("跟我聊天:", value=st.session_state.query, key='query', on_change=submit)

        # 显示所有消息，最新的消息首先显示
        for message in reversed(st.session_state.messages):
            st.write(message)
    else:
        st.write("今天咱们聊得够多了，明天再来吧。")

def submit():
    user_input = st.session_state.query
    if user_input:  # 检查输入是否非空
        result = get_assistant_response(user_input)
        # 将新消息插入列表开头
        st.session_state.messages.insert(0, f"🤖: {result}")
        st.session_state.messages.insert(0, f"👦: {user_input}")
        st.session_state.query = ''  # 清空输入框
        st.session_state.message_count += 1  # 增加消息计数
       
        


  