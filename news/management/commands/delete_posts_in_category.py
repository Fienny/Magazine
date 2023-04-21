from django.core.management.base import BaseCommand, CommandError

from news.models import Category, Post


class Command(BaseCommand):
    help = 'Подсказка вашей команды'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    missing_args_message = 'Enter the category!'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        answer = input(f"Do you really want to delete all posts in {options['category']}? yes/no\n")
        if answer != 'yes':
            self.stdout.write(self.style.ERROR('Denied'))
            return
        try:
            category = Category.objects.get(name=options['category'])
            Post.objects.filter(post_category=category.id).delete()
            self.stdout.write(f"Successfully deleted all posts in {category.name}")
        except Post.DoesNotExist:
            self.stdout.write(f"Could not find category {options['category']}")

