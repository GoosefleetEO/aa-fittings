from allianceauth.services.hooks import get_extension_logger
from django.db import models

from .providers import esi

logger = get_extension_logger(__name__)

class ItemCategoryManager(models.Manager):
    def get_or_create(self, cat_id):
        try:
            cat = self.get(pk=cat_id)
        except:
            cat = self.create_category(cat_id)
            cat = cat[0]

        return cat

    def create_category(self, cat_id) -> tuple:
        """
        Creates ItemCategory from ESI.
        Returns a tuple containing the object and a list of related group_ids
        :param cat_id:
        :return:
        """

        c = esi.client
        cat = c.Universe.get_universe_categories_category_id(category_id=cat_id).result()
        groups = cat.pop('groups')

        obj = self.update_or_create(category_id=cat_id, defaults=cat)

        return obj[0], groups

    def create_category_with_groups(self, cat_id):
        """
        Creates category with all associated groups.
        :param cat_id:
        :return:
        """
        cat, groups = self.create_category(cat_id)

        from .models import ItemGroup
        # Check for groups missing from the category
        missing = ItemGroup.objects.check_groups(groups)

        # Create missing groups.
        for group_id in missing:
            ItemGroup.objects.create_group(group_id, cat_id)

        return cat

    @property
    def groups(self):
        """
        Returns a QueryList of the groups related to this category
        :return:
        """
        from .models import ItemGroup
        grps = ItemGroup.objects.filter(category_id=self)
        return grps


class ItemGroupManager(models.Manager):
    @property
    def types(self):
        """
        Returns a QueryList of the types related to the group.
        :return:
        """
        from .models import Type
        types = Type.objects.filter(group=self)
        return types

    def get_or_create(self, group_id):
        try:
            group = self.get(group_id=group_id)
        except:
            print("Group not found, creating.")
            group = self.create_group(group_id)

        return group

    def check_groups(self, ids: list) -> list:
        """
        Takes a list of group ids, and returns a list of the IDs that do not exist in the
        database.
        :param ids: List of ids to check
        :return: List of group ids missing.
        """
        exist = self.filter(group_id__in=ids).values_list('group_id', flat=True)
        missing = [x for x in ids if x not in exist]
        return missing

    def create_group(self, group_id, passed_id=None):
        """
        Creates group.
        :param group_id:
        :param passed_id:
        :return:
        """
        c = esi.client
        group = c.Universe.get_universe_groups_group_id(group_id=group_id).result()
        cat_id = group.pop('category_id')

        # If called from a method that has already created the category, it should send along the
        # category ID to indicate that it has been created already. We will use this to set the FK
        # and save some DB time.
        if passed_id is None:
            from .models import ItemCategory
            cat = ItemCategory.objects.get_or_create(cat_id)
            group['category'] = cat
        else:
            group['category_id'] = cat_id

        _ = group.pop('types')

        obj = self.update_or_create(group_id=group_id, defaults=group)

        return obj[0]


class TypeManager(models.Manager):
    @staticmethod
    def __get_type_id(self, type_name):
        payload = [type_name]
        c = esi.client
        ids = c.Universe.post_universe_ids(names=payload).result()
        _id = ids.get("inventory_types")[0].get("id")
        return _id

    def create_type(self, type_name):
        _id = self.__get_type_id(self, type_name)
        c = esi.client
        type_result = c.Universe.get_universe_types_type_id(type_id=_id).result()
        type_name = type_result.pop('name')
        type_result['type_name'] = type_name
        attributes = type_result.pop('dogma_attributes')
        effects = type_result.pop('dogma_effects')
        grp_id = type_result.pop('group_id')
        from .models import ItemGroup
        type_result['group'] = ItemGroup.objects.get_or_create(grp_id)

        obj = self.update_or_create(type_id=_id, defaults=type_result)

        # Handle Attributes
        from .models import DogmaAttribute
        if attributes is not None:
            DogmaAttribute.objects.bulk_attributes(attributes, obj[0].pk)

        # Handle Effects
        from .models import DogmaEffect
        if effects is not None:
            DogmaEffect.objects.bulk_effects(effects, obj[0].pk)

        return obj[0]

    def create_type_from_id(self, type_id):
        c = esi.client
        type_result = c.Universe.get_universe_types_type_id(type_id=type_id).result()
        type_name = type_result.pop('name')
        type_result['type_name'] = type_name
        attributes = type_result.pop('dogma_attributes')
        effects = type_result.pop('dogma_effects')
        grp_id = type_result.pop('group_id')
        from .models import ItemGroup
        type_result['group'] = ItemGroup.objects.get_or_create(grp_id)

        obj = self.update_or_create(type_id=type_id, defaults=type_result)

        # Handle Attributes
        from .models import DogmaAttribute
        if attributes is not None:
            DogmaAttribute.objects.bulk_attributes(attributes, obj[0].pk)

        # Handle Effects
        from .models import DogmaEffect
        if effects is not None:
            DogmaEffect.objects.bulk_effects(effects, obj[0].pk)

        return obj[0]

    # Used for the periodic update name task
    def update_type_from_id(self, type_id):
        c = esi.client
        type_result = c.Universe.get_universe_types_type_id(type_id=type_id).result()
        type_name = type_result.pop('name')
        type_result['type_name'] = type_name
        attributes = type_result.pop('dogma_attributes')
        effects = type_result.pop('dogma_effects')
        grp_id = type_result.pop('group_id')
        from .models import ItemGroup
        type_result['group'] = ItemGroup.objects.get_or_create(grp_id)

        obj = self.get(type_id=type_id)
        if obj.type_name != type_name:
            from .models import TypeHistory
            TypeHistory.objects.create(type_id=obj.type_id, type_name=obj.type_name)
            obj.type_name = type_name
            obj.save()
            
        # Handle Attributes
        from .models import DogmaAttribute
        if attributes is not None:
            DogmaAttribute.objects.bulk_attributes(attributes, obj.pk)

        # Handle Effects
        from .models import DogmaEffect
        if effects is not None:
            DogmaEffect.objects.bulk_effects(effects, obj.pk)

        return obj


class DogmaAttributeManager(models.Manager):
    def bulk_attributes(self, attributes, type_pk):
        for attribute in attributes:
            attribute['type_id'] = type_pk
            att = self.update_or_create(type_id=type_pk, attribute_id=attribute['attribute_id'], defaults=attribute)


class DogmaEffectManager(models.Manager):
    def bulk_effects(self, effects, type_pk):
        for effect in effects:
            effect['type_id'] = type_pk
            eff = self.update_or_create(type_id=type_pk, effect_id=effect['effect_id'], defaults=effect)
