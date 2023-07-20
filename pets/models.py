from django.db import models


class Sex(models.TextChoices):
    Male = "Male"
    Female = "Female"
    Default = "Not Informed"


class Pet(models.Model):
    name = models.CharField(max_length=50, null=False)
    age = models.IntegerField()
    weight = models.FloatField()
    sex = models.CharField(max_length=20, choices=Sex.choices, default=Sex.Default)

    group = models.ForeignKey("groups.Group", on_delete=models.PROTECT, related_name="pets")
    traits = models.ManyToManyField("traits.Trait", related_name="pets")
