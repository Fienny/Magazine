from allauth.account.forms import SignupForm
from django.contrib.auth.models import User, Group
from django.db import models
from django.urls import reverse
from news.choices import CHOICES
from simple_history.models import HistoricalRecords


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

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)
    subscribers = models.ManyToManyField(User, related_name='categories')
    history = HistoricalRecords()

    def __str__(self):
        return self.name.title()


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
    history = HistoricalRecords()

    def like(self):
        self.post_rating += 1.0
        self.save()

    def dislike(self):
        self.post_rating -= 1.0
        self.save()

    def preview(self):
        return self.text[:125] + "..."

    def __str__(self):
        return self.heading + ' - ' + self.text

    def get_absolute_url(self):
        return reverse('new_detail', args=[str(self.id)])


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


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
