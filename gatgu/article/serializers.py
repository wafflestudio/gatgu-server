from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    contents = serializers.CharField()
    userprofile = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    article_id = serializers.ReadOnlyField(source='id')
    images = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = Article
        fields = (
            'article_id',
            'title',
            'article_writer_id',
            'userprofile',
            'contents',
            'category',
            'like_count',
            'images',

        )

    def get_userprofile(self, article):
        data = UserProfileSerializer(article.article_writer.userprofile, context=self.context).data
        data.pop('phone')
        try:
            return data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def create(self, validated_data):
        return Article.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    contents = serializers.CharField(required=True, allow_blank=False)
    userprofile = serializers.SerializerMethodField()
    comment_id = serializers.ReadOnlyField(source='id')
    class Meta:
        model = Comment
        fields = (
            'comment_writer_id',
            'userprofile',
            'article_id',
            'comment_id',
            'contents',
            'created_at',
            'updated_at',
        )

    read_only_fields = [
        'comment_id',
        'created_at',
        'updated_at',
    ]

    def get_article_id(self, comment, pk=None):
        article_id = comment.article.objects(pk=pk).id
        return ArticleSerializer(article_id, context='context').data

    def get_userprofile(self, comment):
        data = UserProfileSerializer(comment.comment_writer.userprofile, context=self.context).data
        data.pop('phone')
        return data

