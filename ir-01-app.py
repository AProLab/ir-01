import streamlit as st
import requests
import base64


class FoodCalorieAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def _encode_image(self, file_image):
        """이미지 파일을 base64로 인코딩"""
        file_image.seek(0)
        image_bytes = file_image.read()
        return base64.b64encode(image_bytes).decode("utf-8")

    def _build_prompt(self, base64_image: str):
        """API 요청 메시지 구성"""
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                            당신은 요리 전문가 입니다.
                            입력된 사진을 보고 음식명, 3대 영양소를 [출력 예 1]과 같은 형식으로 출력해 주세요.
                            추가 내용은 출력하지 않습니다.

                            [출력 예 1]
                            :red[**음식**: 라면]\n
                            :blue[**칼로리**: 385kcal]\n
                            **탄수화물**: 55.68g\n
                            **단백질**: 7.9g\n
                            **지방**: 14.54g\n

                            음식 사진이 아니거나, 알수 없는 음식 사진인 경우 [출력 예 2]와 같이 출력해 주세요

                            [출력 예 2]
                            **죄송합니다. 인식할 수 없는 사진입니다.**
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]

    def analyze(self, file_image):
        """음식 사진 분석"""
        base64_image = self._encode_image(file_image)
        messages = self._build_prompt(base64_image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": messages
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


class FoodCalorieApp:
    def __init__(self):
        self.api_key = None
        self.file_image_food = None

    def run(self):
        """Streamlit 앱 실행"""
        st.header("음식 칼로리 분석기")
        self.api_key = st.text_input("OPENAI API KEY를 입력하세요.", type="password")
        self.file_image_food = st.file_uploader("음식 사진만 업로드하세요!", type=['png', 'jpg', 'jpeg'])

        if self.api_key and self.file_image_food:
            analyzer = FoodCalorieAnalyzer(self.api_key)
            st.image(self.file_image_food, width=500)

            with st.spinner("음식 칼로리 분석중..."):
                try:
                    result = analyzer.analyze(self.file_image_food)
                    st.markdown(result)
                except requests.exceptions.RequestException as e:
                    st.error(f"API 요청 오류: {e}")


if __name__ == "__main__":
    app = FoodCalorieApp()
    app.run()