from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from user.models import UserProfile

# Create your tests here.


class PostUserTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )

    def test_post_user_duplicated_username(self):
        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user_incomplete_request(self):
        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user(self):
        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "psjlds",
                "password": "password",
                "first_name": "ae",
                "last_name": "Prk",
                "email": "cs@snu.ac.kr",
                "nickname": "lds",
                "phone": "010-8470-7588",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "psjlds")
        self.assertEqual(data["email"], "cs@snu.ac.kr")
        self.assertEqual(data["first_name"], "ae")
        self.assertEqual(data["last_name"], "Prk")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertIn("token", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "lds")
        self.assertEqual(profile["phone"], "010-8470-7588")

        user_count = User.objects.count()
        self.assertEqual(user_count, 2)

    def test_post_conflict_phone_user(self):
        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "psjlds",
                "password": "password",
                "first_name": "ae",
                "last_name": "Prk",
                "email": "cs@snu.ac.kr",
                "nickname": "lds",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_conflict_nickname_user(self):
        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "psjlds",
                "password": "password",
                "first_name": "ae",
                "last_name": "Prk",
                "email": "cs@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7588",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_empty_nickname(self):

        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "psjlds",
                "password": "password",
                "first_name": "ae",
                "last_name": "Prk",
                "email": "cs@snu.ac.kr",
                "nickname": "",
                "phone": "010-8470-7588",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_empty_phone(self):

        response = self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "psjlds",
                "password": "password",
                "first_name": "ae",
                "last_name": "Prk",
                "email": "cs@snu.ac.kr",
                "nickname": "ee",
                "phone": "",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)


class PutTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )

        self.user_token1 = 'Token ' + \
            Token.objects.get(user__username='cs71107').key

        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cscse",
                "password": "pass",
                "first_name": "Sj",
                "last_name": "Pk",
                "email": "pp@snu.ac.kr",
                "nickname": "cse",
                "phone": "010-8470-7500",
            }),
            content_type='application/json'
        )

        self.user_token2 = 'Token ' + \
            Token.objects.get(user__username='cscse').key

    def test_update_profile(self):
        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(
            '/v1/user/2/',
            json.dumps({
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")

        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
                "nickname": "css",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "css")
        self.assertEqual(profile["phone"], "010-8470-7599")

    def test_update_profile_conflict_nickname(self):
        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
                "nickname": "cse",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_conflict_phone(self):
        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
                "phone": "010-8470-7500",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PutLogin_out_TestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )

        self.user_token = 'Token ' + \
            Token.objects.get(user__username='cs71107').key

    def test_loginout(self):
        response = self.client.put(
            '/v1/user/logout/',
            json.dumps({
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(
            '/v1/user/logout/',
            json.dumps({
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            '/v1/user/login/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertIn("token", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")

    def test_password_changed(self):

        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
                "password": "cspass",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            '/v1/user/logout/',
            json.dumps({
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            '/v1/user/login/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(
            '/v1/user/login/',
            json.dumps({
                "username": "cs71107",
                "password": "cspass",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertIn("token", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")


class GetTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )

        self.user_token1 = 'Token ' + \
            Token.objects.get(user__username='cs71107').key

        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cscse",
                "password": "pass",
                "first_name": "Sj",
                "last_name": "Pk",
                "email": "pp@snu.ac.kr",
                "nickname": "cse",
                "phone": "010-8470-7500",
            }),
            content_type='application/json'
        )

        self.user_token2 = 'Token ' + \
            Token.objects.get(user__username='cscse').key

    def test_get_individual(self):

        me_url = '/v1/user/me/'
        first_url = '/v1/user/'+str(1)+'/'
        second_url = '/v1/user/'+str(2)+'/'

        response = self.client.get(
            first_url,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(
            me_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")

        response = self.client.get(
            first_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")

        response = self.client.get(
            second_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cscse")
        self.assertEqual(data["email"], "pp@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sj")
        self.assertEqual(data["last_name"], "Pk")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cse")
        self.assertEqual(profile["phone"], "010-8470-7500")

    def test_get_put_individual(self):

        me_url = '/v1/user/me/'

        response = self.client.get(
            me_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")

        response = self.client.put(
            '/v1/user/me/',
            json.dumps({
                "nickname": "cscs",
                "phone": "010-8460-7500",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            me_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cscs")
        self.assertEqual(profile["phone"], "010-8460-7500")

    def test_get_users(self):

        user_url = '/v1/user/'

        response = self.client.get(
            user_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        datalist = response.json()

        self.assertEqual(len(datalist), 2)

        data = datalist[0]
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cs71107")
        self.assertEqual(data["email"], "psjlds@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sunjae")
        self.assertEqual(data["last_name"], "Park")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cs")
        self.assertEqual(profile["phone"], "010-8470-7599")

        data = datalist[1]
        self.assertIn("id", data)
        self.assertEqual(data["username"], "cscse")
        self.assertEqual(data["email"], "pp@snu.ac.kr")
        self.assertEqual(data["first_name"], "Sj")
        self.assertEqual(data["last_name"], "Pk")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)

        profile = data["userprofile"]
        self.assertIsNotNone(profile)
        self.assertIn("id", profile)
        self.assertEqual(profile["nickname"], "cse")
        self.assertEqual(profile["phone"], "010-8470-7500")


class WithdrawTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cs71107",
                "password": "password",
                "first_name": "Sunjae",
                "last_name": "Park",
                "email": "psjlds@snu.ac.kr",
                "nickname": "cs",
                "phone": "010-8470-7599",
            }),
            content_type='application/json'
        )

        self.user_token1 = 'Token ' + \
            Token.objects.get(user__username='cs71107').key

        self.client.post(
            '/v1/user/',
            json.dumps({
                "username": "cscse",
                "password": "pass",
                "first_name": "Sj",
                "last_name": "Pk",
                "email": "pp@snu.ac.kr",
                "nickname": "cse",
                "phone": "010-8470-7500",
            }),
            content_type='application/json'
        )

        self.user_token2 = 'Token ' + \
            Token.objects.get(user__username='cscse').key

    def test_withdraw(self):

        user_url = '/v1/user/'

        response = self.client.get(
            user_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        datalist = response.json()

        self.assertEqual(len(datalist), 2)

        withdraw_url = '/v1/user/withdrawal/'

        response = self.client.put(
            withdraw_url,
            json.dumps({
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            user_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token1
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(
            user_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token2
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        datalist = response.json()

        self.assertEqual(len(datalist), 1)

        no_url = user_url+"?tot=no"

        response = self.client.get(
            no_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token2
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        datalist = response.json()

        self.assertEqual(len(datalist), 1)

        yes_url = user_url+"?tot=yes"

        response = self.client.get(
            yes_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        invalid_url = user_url+"?tot=abdc"

        response = self.client.get(
            invalid_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token2
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
