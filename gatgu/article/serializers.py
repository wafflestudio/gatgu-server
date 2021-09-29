import datetime
from django.db.models import Sum, Subquery, OuterRef, Count, IntegerField, Prefetch
from django.db.models.functions import Coalesce

from chat.models import OrderChat, ParticipantProfile
from chat.serializers import OrderChatSerializer
from gatgu.settings import MEDIA_URL
from gatgu.utils import JSTimestampField
from user.serializers import *

from article.models import Article, ArticleImage


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    trading_place = serializers.CharField(required=True)
    product_url = serializers.CharField(required=True, max_length=200)

    price_min = serializers.IntegerField(required=True)
    article_status = serializers.SerializerMethodField()
    order_chat = serializers.SerializerMethodField()

    images = serializers.SerializerMethodField(required=False)
    img_urls = serializers.ListField(child=serializers.CharField(required=False, write_only=True, allow_null=True),
                                     write_only=True, required=False, allow_null=True)

    time_in = JSTimestampField(Article.time_in)
    written_at = JSTimestampField(read_only=True)
    updated_at = JSTimestampField(read_only=True)
    deleted_at = JSTimestampField(read_only=True)

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'description',
            'images',
            'img_urls',

            'trading_place',
            'product_url',
            'time_in',
            'price_min',

            'article_status',
            'order_chat',
            'written_at',
            'updated_at',
            'deleted_at',

        )

    def get_order_chat(self, article):
        return OrderChatSerializer(article.order_chat).data

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat).data
        data['progress_status'] = article.article_status
        return data

    def get_images(self, article):
        return ArticleImageSerializer(article.images, many=True).data

    def validate(self, data):
        return data

    @transaction.atomic
    def create(self, validated_data):
        img_urls = validated_data.pop('img_urls', '')
        article = super(ArticleSerializer, self).create(validated_data)

        for item in img_urls:
            ArticleImage.objects.create(article_id=article.id,
                                        img_url=item)

        OrderChat.objects.create(article=article)
        return article

    @transaction.atomic
    def update(self, article, validated_data):
        img_urls = validated_data.get('img_urls')

        article_image = ArticleImage.objects.filter(article_id=article.id)
        if img_urls:
            print(type(img_urls))
            for item in article_image:
                item.delete()
            for new_img in img_urls:
                ArticleImage.objects.create(article_id=article.id, img_url=new_img)
                # article.images.save()
        return super(ArticleSerializer, self).update(article, validated_data)


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = (
            'id',
            'img_url',
        )


class ParticipantsSummarySerializer(serializers.Serializer):
    cur_price_sum = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'cur_people_sum',
            'cur_price_sum',
        )

    def get_cur_people_sum(self, order_chat):
        return order_chat.count_participant

    def get_cur_price_sum(self, order_chat):
        return order_chat.sum_wish_price


class SimpleArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    price_min = serializers.IntegerField(default=0)
    article_status = serializers.SerializerMethodField()

    images = serializers.SerializerMethodField(required=False)

    time_in = JSTimestampField(Article.time_in)
    updated_at = JSTimestampField(read_only=True)

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'trading_place',
            'images',
            'price_min',
            'time_in',
            'article_status',
            'updated_at',
        )

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat).data
        data['progress_status'] = article.article_status
        return data

    def get_images(self, article):
        # image하나만 받아올 것 ( 대표사진 )
        first_article = article.images

        # 데이터가 없을 때 예외처리 필요
        try:
            return ArticleImageSerializer(first_article, many=True).data[0]
        except IndexError:
            return ArticleImageSerializer('').data

class ArticleRetrieveSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    trading_place = serializers.CharField(required=True)
    product_url = serializers.CharField(required=True, max_length=200)

    price_min = serializers.IntegerField(required=True)
    article_status = serializers.SerializerMethodField()
    order_chat = serializers.SerializerMethodField()

    images = serializers.SerializerMethodField(required=False)
    img_urls = serializers.ListField(child=serializers.CharField(required=False, write_only=True, allow_null=True),
                                     write_only=True, required=False, allow_null=True)

    time_in = JSTimestampField(Article.time_in)
    written_at = JSTimestampField(read_only=True)
    updated_at = JSTimestampField(read_only=True)
    deleted_at = JSTimestampField(read_only=True)
    writer = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = (
            'writer',
            'article_id',
            'title',
            'description',
            'images',
            'img_urls',

            'trading_place',
            'product_url',
            'time_in',
            'price_min',

            'article_status',
            'order_chat',
            'written_at',
            'updated_at',
            'deleted_at',

        )

    def get_order_chat(self, article):
        return OrderChatSerializer(article.order_chat).data

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat).data
        data['progress_status'] = article.article_status
        return data

    def get_images(self, article):
        return ArticleImageSerializer(article.images, many=True).data

    def get_writer(self, article):
        writer = article.writer
        writer_profile = writer.userprofile

        if writer_profile.picture is None:
            profile_img = None
        else:
            profile_img = MEDIA_URL + f'{writer_profile.picture}'
        return dict(id=writer.id, nickname=writer_profile.nickname, profile_img=profile_img)
