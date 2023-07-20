from rest_framework import serializers
from .models import Sex
from traits.serializers import TraitSerializer
from groups.serializers import GroupSerializer


class PetSerializers(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=Sex.choices, default=Sex.Default)

    group = GroupSerializer()
    traits = TraitSerializer(many=True)
