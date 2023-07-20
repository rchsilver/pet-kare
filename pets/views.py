from rest_framework.views import APIView, Response, Request, status
from .serializers import PetSerializers
from .models import Pet
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):

    def post(self, request: Request) -> Response:
        serializer = PetSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = serializer.validated_data
        group = pet.pop("group")
        traits = pet.pop("traits")

        find_group = Group.objects.filter(scientific_name__iexact=group["scientific_name"])
        if find_group:
            find_group = Group.objects.get(scientific_name=dict(group)["scientific_name"])
        else:
            find_group = Group.objects.create(**group)

        new_pet = Pet.objects.create(**pet, group=find_group)

        for trait in traits:
            find_trait = Trait.objects.filter(name__iexact=dict(trait)["name"]).first()

            if not find_trait:
                find_trait = Trait.objects.create(**trait)

            new_pet.traits.add(find_trait)
        serializer = PetSerializers(instance=new_pet)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        if request.query_params:
            trait = request.query_params["trait"]
            pets = Pet.objects.filter(traits__name=trait)
        else:
            pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request)
        serializer = PetSerializers(result_page, many=True)
        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):

    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializers(pet)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializers(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_pet = serializer.validated_data

        if "group" in new_pet:
            group = new_pet.pop("group")
            find_group = Group.objects.filter(scientific_name__iexact=group["scientific_name"])

            if find_group:
                find_group = Group.objects.get(scientific_name=dict(group)["scientific_name"])
            else:
                find_group = Group.objects.create(**group)
            pet.group = find_group

        if "traits" in new_pet:
            traits = new_pet.pop("traits")
            for trait in traits:
                find_trait = Trait.objects.filter(name__iexact=dict(trait)["name"]).first()

                if not find_trait:
                    find_trait = Trait.objects.create(**trait)

                pet.traits.add(find_trait)

        keys = new_pet.items()
        for key, value in keys:
            if key != id:
                setattr(pet, key, value)
        pet.save()
        serializers = PetSerializers(pet)

        return Response(data=serializers.data, status=status.HTTP_200_OK)
