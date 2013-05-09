from django.db import models

class CustomFieldWithGenerator(models.TextField):
    pass

class CustomFieldWithoutGenerator(models.TextField):
    pass
