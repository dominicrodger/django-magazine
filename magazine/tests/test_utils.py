from magazine.models import Article


# Loading from fixtures doesn't call Article.save(), so the
# cleaned_text won't be populated. We therefore need to force
# it here.
def initialise_article_text():
    for article in Article.objects.all():
        if article.text and not article.cleaned_text:
            article.save()


class LoginGuard(object):
    def __init__(self, client, username):
        self.client = client
        self.username = username

    def __enter__(self):
        self.client.login(username=self.username, password='password')

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.logout()
