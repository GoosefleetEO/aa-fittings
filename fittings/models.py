from django.db import models
from model_utils import Choices
from .managers import TypeManager, DogmaAttributeManager, DogmaEffectManager


# Type Model
class Type(models.Model):
    name = models.CharField(max_length=500)
    type_id = models.BigIntegerField(primary_key=True)
    group_id = models.IntegerField()
    published = models.BooleanField(default=False)
    mass = models.FloatField(null=True)
    capacity = models.FloatField(null=True)
    description = models.CharField(max_length=5000, null=False)  # Not sure of the actual max.
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


# Dogma Attribute
class DogmaAttribute(models.Model):
    # 12 - Low Slots | 13 - Med Slots | 14 - High Slots
    # 1137 - Rig Slots | 1367 - Sub System Slots | 2056 - Service Slots
    # 182 | 183 | 184 --- Req Skill 1/2/3
    # 277 - Req. Skill 1 Lvl | 278 | 279 -- Req Skill 1/2 Lvl
    # 1374 - HiSlotModifier | 1375 - MedSlotModifier | 1376 - RigSlotModifier
    type_model = models.ForeignKey(Type, on_delete=models.DO_NOTHING, related_name='dogma_attributes')
    attribute_id = models.IntegerField()
    value = models.FloatField()

    objects = DogmaAttributeManager()

    class Meta:
        default_permissions = ()


# Dogma Effect
class DogmaEffect(models.Model):
    # 11 - Low Power | 12 - High Power | 13 - Med Power
    # 2663 - Rig Slot | 3772 - Subsystem | 6306 - Service Slot
    type_model = models.ForeignKey(Type, on_delete=models.DO_NOTHING, related_name='dogma_effects')
    effect_id = models.IntegerField()
    is_default = models.BooleanField()

    objects = DogmaEffectManager()

    class Meta:
        default_permissions = ()


# Fitting
class Fitting(models.Model):
    description = models.CharField(max_length=1000)  # unsure on max length here
    name = models.CharField(max_length=255, null=False)
    ship_type = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    ship_type_type_id = models.IntegerField()

    class Meta:
        default_permissions = (
            ('access_fittings', 'Can access the fittings module.'),
        )
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
        default_permissions = ()


# Doctrine
class Doctrine(models.Model):
    name = models.CharField(max_length=255, null=False)
    icon_url = models.URLField(null=True)
    fittings = models.ManyToManyField(Fitting, related_name='doctrines')
    description = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(null=True)

    class Meta:
        default_permissions = (
            ("manage", "Can manage doctrines and fits."),
        )

