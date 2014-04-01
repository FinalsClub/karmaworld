from allauth.socialaccount.models import SocialAccount
from django import template

register = template.Library()


class SocialAccountListNode(template.Node):
    def __init__(self, user):
        self.user_string = template.Variable(user)

    def render(self, context):
        try:
            user = self.user_string.resolve(context)
            accounts = [account.provider.title() for account in user.socialaccount_set.all()]
            accounts_string = ', '.join(accounts)
            return accounts_string
        except template.VariableDoesNotExist:
            return ''


def do_social_account_list(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("social_account_list tag requires a single argument")
    return SocialAccountListNode(user)

register.tag('social_account_list', do_social_account_list)

