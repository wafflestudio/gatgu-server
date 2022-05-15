from server import env


class KakaoConstants:
    REDIRECT_URI = "http://localhost:8000/api/account/kakao/signin/callback/"
    CLIENT_ID = env("KAKAO_REST_API_KEY")
