from datetime import datetime, timedelta

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .models import Category, Post


@shared_task
def send_message(cat_id, post_id):
    category = Category.objects.get(pk=cat_id)
    subscribers_list = []
    for i in category.subscribers.all().values("email"):
        for key in i:
            subscribers_list.append(i[key])

    send_mail(
        subject=f'{Post.objects.get(pk=post_id).heading}!',
        message=f'{Post.objects.get(pk=post_id).text}',
        from_email='imfyashya@yandex.ru',
        recipient_list=subscribers_list
    )


@shared_task
def notify_subscribers_weekly():
    all_posts_weekly = Post.objects.all().filter(published_date__range=[f"{datetime.now() - timedelta(days=7)}",
                                                                        f"{datetime.now()}"])
    categories = []
    all_posts_headings = ""
    for post in all_posts_weekly:
        categories.append(post.post_category.all().values("subscribers"))
        all_posts_headings += post.heading + "\n"
    for cat in categories:
        for i in cat:
            for k in i:
                user = User.objects.get(pk=i[k])

                send_mail(
                    subject=f'Good day! There are interesting stuff happened!',
                    message=f'{all_posts_headings}',
                    from_email='imfyashya@yandex.ru',
                    recipient_list=[f"{user.email}"]
                )
