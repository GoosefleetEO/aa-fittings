from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Subquery, OuterRef
from model_utils import Choices

from .managers import TypeManager, DogmaAttributeManager, DogmaEffectManager, ItemCategoryManager, ItemGroupManager


# Category Model
class ItemCategory(models.Model):
    category_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    published = models.BooleanField(default=True)

    objects = ItemCategoryManager()

    class Meta:
        default_permissions = ()


# Group Model
class ItemGroup(models.Model):
    group_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    published = models.BooleanField(default=True)

    objects = ItemGroupManager()

    class Meta:
        default_permissions = ()


# Type Model
class Type(models.Model):
    type_name = models.CharField(max_length=500)
    type_id = models.BigIntegerField(primary_key=True)
    # group_id = models.IntegerField()    # This is essentially a FK field.
    group = models.ForeignKey(ItemGroup, on_delete=models.CASCADE, null=True)
    published = models.BooleanField(default=False)
    mass = models.FloatField(null=True)
    capacity = models.FloatField(null=True)
    description = models.CharField(max_length=5000, null=True)  # Not sure of the actual max.
    volume = models.FloatField(null=True)
    packaged_volume = models.FloatField(null=True)
    portion_size = models.IntegerField(null=True)
    radius = models.FloatField(null=True)
    graphic_id = models.IntegerField(null=True)
    icon_id = models.IntegerField(null=True)
    market_group_id = models.IntegerField(null=True)

    objects = TypeManager()

    class Meta:
        default_permissions = ()


class TypeHistory(models.Model):
    type_id = models.BigIntegerField()
    type_name = models.CharField(max_length=500)

    class Meta:
        default_permissions = ()


# Dogma Attribute
class DogmaAttribute(models.Model):
    # 12 - Low Slots | 13 - Med Slots | 14 - High Slots
    # 1137 - Rig Slots | 1367 - Sub System Slots | 2056 - Service Slots
    # 182 | 183 | 184 --- Req Skill 1/2/3
    # 277 - Req. Skill 1 Lvl | 278 | 279 -- Req Skill 1/2 Lvl
    # 1374 - HiSlotModifier | 1375 - MedSlotModifier | 1376 - RigSlotModifier
    type = models.ForeignKey(Type, on_delete=models.DO_NOTHING, related_name='dogma_attributes')
    attribute_id = models.IntegerField()
    value = models.FloatField()

    objects = DogmaAttributeManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(fields=('attribute_id', 'type'), name='unique_type_and_attribute_id')
        ]


# Dogma Effect
class DogmaEffect(models.Model):
    # 11 - Low Power | 12 - High Power | 13 - Med Power
    # 2663 - Rig Slot | 3772 - Subsystem | 6306 - Service Slot
    type = models.ForeignKey(Type, on_delete=models.DO_NOTHING, related_name='dogma_effects')
    effect_id = models.IntegerField()
    is_default = models.BooleanField()

    objects = DogmaEffectManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(fields=('effect_id', 'type'), name='unique_type_and_effect_id')
        ]


# Fitting
class Fitting(models.Model):
    description = models.TextField(max_length=500)
    name = models.CharField(max_length=255, null=False)
    ship_type = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    ship_type_type_id = models.IntegerField()

    def __str__(self):
        return "{} ({})".format(self.ship_type.type_name, self.name)

    @property
    def eft(self):
        types = Type.objects.filter(type_id=OuterRef('type_id'))
        items = FittingItem.objects.filter(fit=self).annotate(item_name=Subquery(types.values('type_name')))

        eft = '[' + self.ship_type.type_name + ', ' + self.name + ']\n\n'

        temp = {'Cargo': [], 'FighterBay': [], 'DroneBay': []}
        
        slots = [
            {'key': 'LoSlot', 'range': 8},
            {'key': 'MedSlot', 'range': 8},
            {'key': 'HiSlot', 'range': 8},
            {'key': 'RigSlot', 'range': 3},
            {'key': 'SubSystemSlot', 'range': 4},
            {'key': 'ServiceSlot', 'range': 8}  # This is likely much higher than the actual max.
        ]
        
        for item in items:
            if item.flag == 'Cargo':
                temp['Cargo'].append(item)
            elif item.flag == 'FighterBay':
                temp['FighterBay'].append(item)
            elif item.flag == 'DroneBay':
                temp['DroneBay'].append(item)
            else:
                temp[item.flag] = item.item_name

        for slot in slots:
            is_empty = True
            for i in range(0, slot['range']):
                key = slot['key'] + str(i)
                if key in temp:
                    eft += temp[key] + '\n'
                    is_empty = False
            if not is_empty:
                eft += '\n'

        slots = [
            'FighterBay',
            'DroneBay',
            'Cargo'
        ]

        for slot in slots:
            if slot in temp:
                eft += '\n\n'
                for item in temp[slot]:
                    eft += item.item_name + ' x' + str(item.quantity) + '\n'

        eft += '\n'
        
        return eft

    class Meta:
        default_permissions = (())
        permissions = (('access_fittings', 'Can access the fittings module.'),)
        unique_together = (
            ('ship_type_type_id', 'name'),
        )


# Fitting items
class FittingItem(models.Model):
    fit = models.ForeignKey(Fitting, on_delete=models.CASCADE, related_name='items')
    _flag_enum = Choices('Cargo', 'DroneBay', 'FighterBay', 'HiSlot0', 'HiSlot1', 'HiSlot2',
                         'HiSlot3', 'HiSlot4', 'HiSlot5', 'HiSlot6', 'HiSlot7', 'Invalid',
                         'LoSlot0', 'LoSlot1', 'LoSlot2', 'LoSlot3', 'LoSlot4', 'LoSlot5',
                         'LoSlot6', 'LoSlot7', 'MedSlot0', 'MedSlot1', 'MedSlot2', 'MedSlot3',
                         'MedSlot4', 'MedSlot5', 'MedSlot6', 'MedSlot7', 'RigSlot0', 'RigSlot1',
                         'RigSlot2', 'ServiceSlot0', 'ServiceSlot1', 'ServiceSlot2', 'ServiceSlot3',
                         'ServiceSlot4', 'ServiceSlot5', 'ServiceSlot6', 'ServiceSlot7', 'SubSystemSlot0',
                         'SubSystemSlot1', 'SubSystemSlot2', 'SubSystemSlot3')
    flag = models.CharField(max_length=25, choices=_flag_enum, default='Invalid')
    quantity = models.IntegerField(default=1)
    type_fk = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    type_id = models.IntegerField()

    class Meta:
        default_permissions = (())


# Doctrine
class Doctrine(models.Model):
    name = models.CharField(max_length=255, null=False)
    icon_url = models.URLField(null=True)
    fittings = models.ManyToManyField(Fitting, related_name='doctrines')
    description = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        default_permissions = (())
        permissions = (("manage", "Can manage doctrines and fits."),)


# Unified Category
class Category(models.Model):
    name = models.CharField(max_length=255, null=False)
    color = models.TextField(max_length=20, default="#FFFFFF")  # Tag Color

    fittings = models.ManyToManyField(Fitting, blank=True, related_name="category",
                                      help_text="Fittings only need to be tagged with a category if they are "
                                                "not included in any doctrines, or if they need to be labled "
                                                "in addition to their doctrine's category.")
    doctrines = models.ManyToManyField(Doctrine, blank=True, related_name="category",
                                       help_text="All fittings in a doctrine will be treated as if they are in the "
                                                 "doctrine's category.")

    groups = models.ManyToManyField(Group, blank=True, related_name="access_restricted_category",
                                    help_text="Groups listed here will be able to access fits and doctrines"
                                              " listed under this category. If a category has no groups listed"
                                              " then it is considered an public category, accessible to anyone"
                                              " with permission to access permissions to the fittings module.")

    def __str__(self):
        return f"Category: {self.name}"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        default_permissions = (())


# Unified Category
class ServerVersion(models.Model):
    id = models.BigIntegerField(primary_key=True)

    def __str__(self):
        return f"Server Version: {self.id}"

    class Meta:
        verbose_name = "ServerVersion"
        default_permissions = (())
