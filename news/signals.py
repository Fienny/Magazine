from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PostCategory, Post, Author
from django.db.models.functions import Now


@receiver(m2m_changed, sender=PostCategory)
def mass_sender(sender, instance, action, **kwargs):
    if action == "post_add":
        categories = instance.post_category.all().values("subscribers")
        subscribers_list = []
        for i in categories:
            for key in i:
                user = User.objects.all().get(pk=i[key])
                subscribers_list.append(user.email)

        send_mail(
            subject=f'{instance.heading}!',
            message=f'{instance.text}',
            from_email='imfyashya@yandex.ru',
            recipient_list=subscribers_list
        )


@receiver(pre_save, sender=Post)
def check_for_saves(sender, instance, **kwargs):
    current_author = instance.author_id
    recipient_author = Author.objects.get(id=current_author).user.email
    l_check = Post.objects.all().filter(author=Author.objects.get(id=current_author),
                                        published_date__range=[f"{datetime.now()-timedelta(hours=24)}", f"{datetime.now()}"]
                                        )
    if len(l_check) > 3:
        send_mail(
                subject="Error",
                message="Sorry, you can't save more than 3 post per day(",
                from_email='imfyashya@yandex.ru',
                recipient_list=[f"{recipient_author}"]
        )
        raise Exception("Sorry, you can't save more than 3 post per day(")
