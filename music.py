import streamlit as st
import openai
import os
from dotenv import load_dotenv

# .env 파일 내의 변수들을 로드합니다.
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)  # 디버깅 용도로 사용

# TTM 프롬프트 생성 함수
def generate_ttm_prompt(intent):
    prompt = f"""
    You are a prompt engineer.
    The user aims to realize imagined audio through a Text-to-Music(TTM) model.
    However, since the user is not an expert in the audio field, it is difficult for them to write a detailed TTM prompt to input into the TTA model.
    So, you need to refine the user’s vague prompt into a more specific TTM prompt.
    The audio attributes that can be described through text include: tone, pitch, rhythm, atmosphere, style, and all the audio details.
    But, do not include following audio attributes: audio length, vocal.
    **Output Cautions**
    - Only generate prompts for audio attributes that the user mentions.
    - Don't say anything. Just say refined TTM prompt.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": intent}
        ]
    )
    return response['choices'][0]['message']['content']  # Ensure this is indented properly

# 후속 질문 생성 함수
def follow_up_questions(intent):
    prompt = f"""
    The user aims to realize imagined audio through a Text-to-Music(TTM) model.
    However, since the user is not an expert in the audio field, it is difficult for them to write a detailed TTM prompt to input into the TTA model.
    So, you need to identify the missing audio attributes in the user’s vague prompt and ask follow-up questions to gather additional information about the lacking audio attributes.
    The audio attributes that can be described through text include: tone, pitch, rhythm, atmosphere, style, and all the audio details.
    But, do not include following audio attributes: audio length, vocal.
    Your output should be like: 
        1) [ Attribution Needs Modification based on user's intent:[{intent}] ]
            - [ follow-up response recommendations ]
        2) [ Unmentioned Attribution based on user's intent:[{intent}] ]
            - [ follow-up response recommendations ]
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": intent}
        ]
    )
    return response['choices'][0]['message']['content']

# 피드백 반영 프롬프트 수정 함수
def refine_prompt(llmprompt, user_feedback):
    prompt = f"""
    You are the prompt engineer, and you will receive two pieces of information:
    - user_feedback: the user's feedback, i.e., the intent that was further refined by listening to the audio generated just before.
    - llmprompt: The Text-to-Music(TTM) prompt you refined just before, i.e., the TTM prompt that led to the creation of user_feedback.
    Your job as a prompt engineer is to:
    - Modify [{llmprompt}] to correspond to [{user_feedback}], and generate the modified TTM prompt.
    Don't say anything. Just say modified TTM prompt.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_feedback}
        ]
    )
    return response['choices'][0]['message']['content']

# Streamlit 애플리케이션
def main():
    st.title("Text-to-music Chatbot")

    user_input = st.text_input("원하는 음악을 입력하세요 (종료하려면 'exit' 입력):")

    if user_input.lower() == 'exit':
        st.write("프로그램을 종료합니다.")
        return

    if user_input:
        # TTM 프롬프트 생성
        ttm_prompt = generate_ttm_prompt(user_input)
        st.write(f"TTM 프롬프트: {ttm_prompt}")

        # 후속 질문 생성
        follow_up = follow_up_questions(user_input)
        st.write("후속 질문:")
        st.write(follow_up)

        # 피드백 입력
        user_feedback = st.text_input("피드백 입력:")
        if user_feedback:
            refined_prompt = refine_prompt(ttm_prompt, user_feedback)
            st.write(f"수정된 TTM 프롬프트: {refined_prompt}")

        # 항상 지정된 WAV 파일 제공
        audio_file_path = "/Users/eo-seonyoung/Downloads/generated_audio_20241106_050303.wav"
        if os.path.exists(audio_file_path):
            st.audio(audio_file_path)
            st.write("음악 파일을 제공합니다.")
        else:
            st.write("음악 파일이 존재하지 않습니다.")

# main 함수 호출
if __name__ == "__main__":
    main()