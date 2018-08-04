from django.db import models


class Options(models.Model):

    key = models.CharField(max_length = 250, unique=True)
    value = models.TextField()
    label = models.CharField(max_length = 500)


class Departments(models.Model):

    name = models.CharField(max_length = 250, unique=True)
    short_name = models.CharField(max_length = 10)

    def __str__(self):
        return "%s (%s)" % (self.name, self.short_name)

class DepartmentBranches(models.Model):

    name = models.CharField(max_length=250, unique=True)
    short_name = models.CharField(max_length = 10)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)

    def __str__(self):
        return "%s (%s)" % (self.name, self.short_name)