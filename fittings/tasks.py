from .models import Fitting, FittingItem, Type, DogmaEffect, DogmaAttribute
from esi.clients import esi_client_factory
from celery import shared_task


class EftParser:
    def __init__(self, eft_text):
        self.eft_lines = eft_text.strip().splitlines()

    def parse(self):
        modules = []
        cargo_drone = []
        ship_type = ''
        fit_name = ''
        counter = 0     # Slot flag number

        for line in self.eft_lines:
            if line == '':
                counter = 0
                continue

            if line.startswith('['):
                if ', ' in line:
                    ship_type, fit_name = line[1:-1].split(', ')
                    continue

                if 'empty' in line.strip('[]').lower():
                    continue

            else:
                if ',' in line:
                    module, charge = line.split(',')
                    modules.append({'name': module, 'charge': charge.strip(), 'count': counter})
                else:
                    quantity = line.split()[-1]  # Quantity will always be the last element, if it is there.

                    if 'x' in quantity and quantity[1:].isdigit():
                        item_name = line.strip(quantity).strip()
                        cargo_drone.append({'name': item_name, 'quantity': int(quantity.strip('x'))})
                    else:
                        modules.append({'name': line.strip(), 'charge': '', 'count': counter})
            counter += 1

        return {'ship': ship_type, 'name': fit_name, 'modules': modules, 'cargo_drones': cargo_drone}


def _get_type(type_name):
    try:
        type_obj = Type.objects.get(name=type_name)
    except:
        type_obj = Type.objects.create_type(type_name)
    return type_obj


@shared_task()
def create_fitting_item(fit, item):
    count = None
    quantity = None
    if 'count' in item:
        count = item['count']

    type_obj = _get_type(item['name'])

    # Dogma Effects
    flags = {11: 'LoSlot', 12: 'HiSlot', 13: 'MedSlot', 2663: 'RigSlot', 3772: 'SubSystemSlot', 6306: 'ServiceSlot'}
    effects = type_obj.dogma_effects.filter(effect_id__in=flags).values_list('effect_id', flat=True)
    effects = list(effects)
    if count is None:
        flag = 'Cargo'
        quantity = item['quantity']
    else:
        flag = flags[effects[0]] + str(count)

    item = FittingItem.objects.create(flag=flag, quantity=quantity if quantity else 1, type_fk=type_obj,
                                      type_id=type_obj.pk, fit=fit)


@shared_task
def create_fit(eft_text, description=None):
    parsed_eft = EftParser(eft_text).parse()

    def __create_fit(ship_type, name, description):
        type_obj = _get_type(ship_type)
        fit = Fitting.objects.create(ship_type=type_obj, ship_type_type_id=type_obj.pk,
                                     name=name, description=description)
        return fit

    fit = __create_fit(parsed_eft['ship'], parsed_eft['name'], description)

    for module in parsed_eft['modules']:
        create_fitting_item(fit, module)

    for item in parsed_eft['cargo_drones']:
        create_fitting_item(fit, item)


@shared_task
def populate_types():
    # Get all the type IDs.
    c = esi_client_factory(version='latest')

    operation = c.Universe.get_universe_types()
    operation.also_return_response = True
    _, response = operation.result()
    pages = int(response.headers['x-pages'])

    for page in range(1, pages + 1):
        types_page.delay(page)


@shared_task
def types_page(page):
    c = esi_client_factory(version='latest')

    type_ids = c.Universe.get_universe_types(page=page).result()

    dogma = {}
    types = []
    for type_id in type_ids:
        try:
            type_result = c.Universe.get_universe_types_type_id(type_id=type_id).result()
            if type_result.get('published') is False:
                # Unpublished items are unlikely to be in fits
                continue
            attributes = type_result.pop('dogma_attributes')
            effects = type_result.pop('dogma_effects')

            types.append(Type(**type_result))
            dogma[type_id] = {'effects': effects, 'attributes': attributes}
        except:
            pass
    Type.objects.bulk_create(types, batch_size=500)

    attrs = []
    effects = []
    for type_id, dogma in dogma.items():
        if dogma['effects'] is not None:
            for effect in dogma['effects']:
                effect['type_model_id'] = type_id
                effects.append(DogmaEffect(**effect))

        if dogma['attributes'] is not None:
            for attribute in dogma['attributes']:
                attribute['type_model_id'] = type_id
                attrs.append(DogmaAttribute(**attribute))

    DogmaAttribute.objects.bulk_create(attrs, batch_size=500)
    DogmaEffect.objects.bulk_create(effects, batch_size=500)

