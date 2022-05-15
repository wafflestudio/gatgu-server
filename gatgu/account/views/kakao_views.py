from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from gatgu.constants import KakaoConstants
from django.shortcuts import redirect
import requests


class KakaoSignInAPIView(APIView):
    def get(self, request):
        client_id = KakaoConstants.CLIENT_ID
        redirect_uri = KakaoConstants.REDIRECT_URI
        kakao_auth_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        return redirect(
            f"{kakao_auth_api}&client_id={client_id}&redirect_uri={redirect_uri}"
        )


class KakaoSignInCallBackAPIView(APIView):
    def get(self, request):
        auth_code = request.query_params.get("code")
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": KakaoConstants.CLIENT_ID,
            "redirection_uri": "http://localhost:8000/accounts/signin/kakao/callback",
            "code": auth_code,
        }
        token_response = requests.post(kakao_token_api, data=data)
        token_info = token_response.json()
        access_token = token_info.get("access_token")
        user_info_response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer ${access_token}"},
        )

        return Response(
            status=status.HTTP_200_OK, data={"user_info": user_info_response}
        )
