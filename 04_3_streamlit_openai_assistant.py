from openai import OpenAI
import streamlit as st
import time

"""
assistant를 사용한다고 해서, thread에 있는 메세지를 뽑아오는지 알았더니 그게 아님
여기 사이트에서 질문, 답변 한것만 나오게함 > session_state 사용

문제점 : 1명을 위한 서비스 > 스레드를 새로 생성해 주면 되겠네

"""

assistant_id = "asst_tyL2gmT5xWTtpdmZ5KmEwR56"
# thread_id = "thread_eQs1aOxBnhE5G7m4v3ekm2yl"

with st.sidebar:
    st.link_button("네이버 바로가기", "https://www.naver.com")

    iframe_html = """<iframe src="https://ads-partners.coupang.com/widgets.html?id=776180&template=banner&trackingCode=AF3633158&subId=&width=300&height=250" width="300" height="250" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" browsingtopics></iframe>"""
    st.markdown(iframe_html, unsafe_allow_html=True)

    st.info("이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.")

    openai_api_key = st.text_input("OpenAI API KEY", type="password")
    client = OpenAI(api_key=openai_api_key)
    thread_id = st.text_input("Thread ID", value="thread_eQs1aOxBnhE5G7m4v3ekm2yl")
    
    if st.button("Create a new Thread"):    # 새로운 스레드 id make
        thread = client.beta.threads.create()

        thread_id = thread.id
        st.subheader(f"{thread_id}", divider='rainbow')
        st.info("새로운 스레드가 생성되었습니다.")

st.title("My ChatBot")

# 유지되는 변수 만들기
if "messages" not in st.session_state:
    st.session_state['messages'] = [{"role" : "assistant", "content" : "선생님한테 무엇이든 물어보세요"}]

print(f"st.session_state\n{st.session_state}")
print()

# 저장된 채팅창에 질문 답변 출력하기
for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

prompt = st.chat_input("user: ")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 질문 한 내용 변수에 저장 
    st.chat_message("user").write(prompt)
    
    # step: 메세지 보내기 assistant에게
    message = client.beta.threads.messages.create(
        # thread_id=thread.id, >> 원래 코드
        thread_id = thread_id,
        role="user",
        content=prompt
    )

    # step : run 실행
    run = client.beta.threads.runs.create(  
        #? 와 시발, 공식문서에 create_and_poll 이라고 되어있는데, 이게 오류네, 김플거 보고 에러처리함 create 로 바꿈 
        thread_id=thread_id,
        assistant_id=assistant_id,
        # instructions="Please address the user as Jane Doe. The user has a premium account."
        # 여기도 지침이 있는데, 사용안하는게 좋음, 맨처음 지침보다 우선할수 있음 (when creating an assistant)
    )

    while True:     # 답변체크 for문
        # 이거는 runs을 검색하는 놈이네
        run = client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = run.id
        )

        if run.status == 'completed':   # completed = 메세지 응답 완료상태
            break
        else:
            time.sleep(3)

    # response 메세지 받아오기 
    thread_message = client.beta.threads.messages.list(
        thread_id = thread_id
    )

    assistatn_content = thread_message.data[0].content[0].text.value    # 가장 최근 메세지
    st.session_state['messages'].append({"role" : "assistant", "content" : assistatn_content})
    st.chat_message("assistant").write(assistatn_content)


