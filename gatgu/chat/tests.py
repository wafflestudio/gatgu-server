from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from chat.models import OrderChat, ChatMessage, ParticipantProfile
from article.models import Article
import datetime
import json

# Create your tests here.

class ChatTestCase(TestCase):
    User = get_user_model()

    @classmethod
    def setUpTestData(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='user1', password='pass1')
        self.user.is_active = True
        self.user.save()
        self.article = Article(writer=self.user, title='title1', description='des1', location='loc1', product_url='purl1', thumbnail_url='turl1',
        people_min=4, price_min=5000)#'''time_max=datetime.timezone(timedelta(0)), time_remaining=datetime.timezone.now()''')
        self.article.save()
        self.orderchat = OrderChat(article=self.article, order_status='stat1', tracking_number='track1', required_people=5, cur_people=0)
        self.orderchat.save()
        self.participant = ParticipantProfile(chat=self.orderchat, participant=self.user, joined_at=datetime.datetime.now(), pay_status='pay1')
        self.participant.save()
        self.message = ChatMessage(text='text1', sent_by=self.user, chat=self.orderchat, type='type1', media='murl1')
        self.message.save()
        self.client = Client(enforce_csrf_checks=True)
        
    def test_user(self):
        user = list(self.User.objects.filter(username='user1').values())
        self.assertEqual(len(user), 1)
    
    def test_get_chats(self):
        #self.client = Client(enforce_csrf_checks=True)
        #self.client.login(username='user1', password='pass1')
        response = self.client.get('/v1/chat/')
        self.assertEqual(response.status_code, 401)

        self.client.login(username='user1', password='pass1')
        response = self.client.get('/v1/chat/')
        self.assertEqual(response.status_code, 200)
    
    def test_get_chat(self):
        #self.client = Client(enforce_csrf_checks=True)
        #self.client.login(username='user1', password='pass1')
        response = self.client.get('/v1/chat/1/')
        self.assertEqual(response.status_code, 401)

        self.client.login(username='user1', password='pass1')
        response = self.client.get('/v1/chat/1/')
        self.assertEqual(response.status_code, 200)

    def test_join_chat(self):
        #self.client = Client(enforce_csrf_checks=True)
        response = self.client.put('/v1/chat/1/join/')
        self.assertEqual(response.status_code, 401)
        
        self.client.login(username='user1', password='pass1')
        response = self.client.put('/v1/chat/1/join/')
        self.assertEqual(response.status_code, 200)
    
    def test_out_chat(self):
        #self.client = Client(enforce_csrf_checks=True)
        self.client.login(username='user1', password='pass1')
        response = self.client.put('/v1/chat/1/out/')
        self.assertEqual(response.status_code, 200)
    
    def test_post_message(self):
        message = {'text': 'text_sent', 'image_url':'url_sent'}
        
        response = self.client.post('/v1/chat/1/messages/', json.dumps(message), content_type = 'application/json')
        self.assertEqual(response.status_code, 401)

        self.client.login(username='user1', password='pass1')
        response = self.client.post('/v1/chat/1/messages/', json.dumps(message), content_type = 'application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_get_message(self):
        response = self.client.get('/v1/chat/message/1/')
        self.assertEqual(response.status_code, 401)

        self.client.login(username='user1', password='pass1')
        response = self.client.get('/v1/chat/message/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_participants(self):
        response = self.client.get('/v1/chat/1/participants/')
        self.assertEqual(response.status_code, 401)

        self.client.login(username='user1', password='pass1')
        response = self.client.get('/v1/chat/1/participants/')
        self.assertEqual(response.status_code, 200)

    def test_set_status(self):
        new_status = {'status': 'complete'}
        
        response = self.client.put('/v1/chat/1/set_status/', json.dumps(new_status))
        self.assertEqual(response.status_code, 401)

        self.client.login(username='user1', password='pass1')
        response = self.client.put('/v1/chat/1/set_status/', json.dumps(new_status))
        self.assertEqual(response.status_code, 200)

    

