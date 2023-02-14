from django.contrib.auth.models import User
from django.db import models
from news.choices import CHOICES


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.FloatField(default=0)

    def update_rating(self):
        rating_author1 = 0
        rating_author2 = 0
        l = self.user.comment_set.all().values('user_comment')
        for item in l:
            for key in item:
                rating_author1 += float(item[key])

        for item in Comment.objects.all().values('comment_rating'):
            for key in item:
                rating_author2 += float(item[key])

        self.author_rating = 3 * rating_author1 + rating_author2
        self.save()


class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)


class Post(models.Model):
    article = "AR"
    news = "NW"

    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    choice = models.CharField(max_length=2, choices=CHOICES, default=news)
    published_date = models.DateTimeField(auto_now_add=True)
    post_category = models.ManyToManyField("Category", through="PostCategory")
    heading = models.CharField(blank=False, unique=True, max_length=255)
    text = models.TextField(blank=False)
    post_rating = models.FloatField(default=0)

    def like(self):
        self.post_rating += 1.0
        self.save()

    def dislike(self):
        self.post_rating -= 1.0
        self.save()

    def preview(self):
        return self.text[:125] + "..."


class PostCategory(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)


class Comment(models.Model):
    post_comment = models.ForeignKey("Post", on_delete=models.CASCADE)
    user_comment = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField(blank=False)
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_rating = models.FloatField(default=0)

    def like(self):
        self.comment_rating += 1.0
        self.save()

    def dislike(self):
        self.comment_rating -= 1.0
        self.save()
