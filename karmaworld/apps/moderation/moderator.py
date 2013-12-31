from django.contrib.admin.sites import AdminSite

# Create a second administration site for use by moderators
site = AdminSite('moderator')
