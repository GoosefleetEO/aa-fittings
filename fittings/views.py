from allianceauth.services.hooks import get_extension_logger
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Subquery, OuterRef, Count, Q, Prefetch, F
from django.shortcuts import render, redirect
from esi.decorators import token_required

from .models import Doctrine, Fitting, Type, FittingItem, Category
from .providers import esi
from .tasks import create_fit, update_fit

logger = get_extension_logger(__name__)


# Create your views here.
def _build_slots(fit):
    ship = fit.ship_type
    attributes = (12, 13, 14, 1137, 1367, 2056)

    t3c = ship.dogma_attributes.filter(attribute_id=1367).exists()

    attributes = ship.dogma_attributes.filter(attribute_id__in=attributes)

    slots = {'low': 0, 'med': 0, 'high': 0}
    for attribute in attributes:
        if attribute.attribute_id == 1367:
            subAttbs = (1374, 1375, 1376)
            slots['sub'] = 4
            if t3c:
                for item in FittingItem.objects.filter(fit=fit).exclude(flag='Cargo'):
                    attbs = item.type_fk.dogma_attributes.filter(attribute_id__in=subAttbs)
                    for attb in attbs:
                        if attb.attribute_id == 1374:
                            slots['high'] += int(attb.value)
                        if attb.attribute_id == 1375:
                            slots['med'] += int(attb.value)
                        if attb.attribute_id == 1376:
                            slots['low'] += int(attb.value)

        elif attribute.attribute_id == 12:
            slots['low'] += int(attribute.value)
        elif attribute.attribute_id == 13:
            slots['med'] += int(attribute.value)
        elif attribute.attribute_id == 14:
            slots['high'] += int(attribute.value)
        elif attribute.attribute_id == 1137:
            slots['rig'] = int(attribute.value)

    return slots


def _check_fit_access(user, fit_id: int) -> bool:
    fit_id = int(fit_id)
    logger.debug(f"Checking user {user.pk} access to fit {fit_id}")
    if user.has_perm('fittings.manage'):
        logger.debug(f"User {user.pk} has manage permissions, returning True.")
        return True
    groups = user.groups.all()
    fits = Fitting.objects.filter(
        Q(Q(category__groups__in=groups) |
          Q(category__isnull=True) |
          Q(category__groups__isnull=True)) &
        Q(Q(doctrines__category__groups__isnull=True) |
          Q(doctrines__category__groups__in=groups) |
          Q(doctrines__category__isnull=True))).filter(pk=fit_id).exists()
    logger.debug(f"returning {fits}")
    return fits


@permission_required('fittings.access_fittings')
@login_required()
def dashboard(request):
    doc_dict = {}
    if request.user.has_perm('fittings.manage'):
        docs = Doctrine.objects.prefetch_related(Prefetch('fittings', Fitting.objects.select_related('ship_type')))\
            .prefetch_related('category').all()
    else:
        docs = Doctrine.objects.prefetch_related('category')\
            .prefetch_related(Prefetch('fittings', Fitting.objects.select_related('ship_type')))\
            .filter(
                Q(category__groups__in=request.user.groups.all()) |
                Q(category__isnull=True) |
                Q(category__groups__isnull=True))
    for doc in docs:
        fits = []
        ids = []
        for fit in doc.fittings.all():
            if fit.ship_type_type_id not in ids:
                fits.append(fit)
                ids.append(fit.ship_type_type_id)
        doc_dict[doc.pk] = fits
    ctx = {'docs': docs, 'doc_dict': doc_dict}
    return render(request, 'fittings/dashboard.html', context=ctx)


@permission_required('fittings.manage')
@login_required()
def add_fit(request):
    ctx = {}
    if request.method == 'POST':
        etf_text = request.POST['eft']
        description = request.POST['description']

        create_fit.delay(etf_text, description)
        # Add success message, with note that it may take some time to see the fit on the dashboard.
        return redirect('fittings:dashboard')

    return render(request, 'fittings/add_fit.html', context=ctx)


@permission_required('fittings.manage')
@login_required()
def edit_fit(request, fit_id):
    try:
        fit = Fitting.objects.get(pk=fit_id)
        
    except Fitting.DoesNotExist:
        messages.warning(request, 'Fit not found!')

        return redirect('fittings:dashboard')

    if request.method == 'POST':
        etf_text = request.POST['eft']
        description = request.POST['description']

        update_fit.delay(etf_text, fit_id, description)
        # Add success message, with note that it may take some time to see the fit on the dashboard.
        return redirect('fittings:view_fit', fit_id)

    ctx = {'fit': fit}
    return render(request, 'fittings/edit_fit.html', context=ctx)


@permission_required('fittings.access_fittings')
@login_required()
def view_fit(request, fit_id):
    ctx = {}
    try:
        fit = Fitting.objects.prefetch_related('category', 'doctrines', 'doctrines__category').get(pk=fit_id)
    except Fitting.DoesNotExist:
        messages.warning(request, 'Fit not found!')

        return redirect('fittings:dashboard')

    # Ensure that the character should have access to the fitting.
    access = _check_fit_access(request.user, fit_id)

    if not access:
        messages.warning(request, 'You do not have access to that fit.')

        return redirect('fittings:dashboard')

    types = Type.objects.filter(type_id=OuterRef('type_id'))
    items = FittingItem.objects.filter(fit=fit).annotate(item_name=Subquery(types.values('type_name')))

    fittings = {'Cargo': [], 'FighterBay': [], 'DroneBay': []}

    for item in items:
        if item.flag == "Cargo":
            fittings['Cargo'].append(item)
        elif item.flag == "DroneBay":
            fittings['DroneBay'].append(item)
        elif item.flag == "FighterBay":
            fittings['FighterBay'].append(item)
        else:
            fittings[item.flag] = item

    ctx['doctrines'] = fit.doctrines.all()
    ctx['slots'] = _build_slots(fit)
    ctx['fit'] = fit
    ctx['fitting'] = fittings

    # Build Doctrine Category Dict
    cats = []
    ids = []
    for doc in ctx['doctrines']:
        for cat in doc.category.all():
            if cat.pk not in ids:
                cats.append(cat)
                ids.append(cat.pk)
    for cat in fit.category.all():
        if cat.pk not in ids:
            cats.append(cat)
            ids.append(cat.pk)
    del ids
    ctx['cats'] = cats

    return render(request, 'fittings/view_fit.html', context=ctx)


@permission_required('fittings.manage')
@login_required()
def add_doctrine(request):
    ctx = {}
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        icon_url = request.POST['iconSelect']
        fitSelect = [int(fit) for fit in request.POST.getlist('fitSelect')]

        fits = Fitting.objects.filter(pk__in=fitSelect)
        d = Doctrine(name=name, description=description, icon_url=icon_url)
        d.save()
        for fitting in fits:
            d.fittings.add(fitting)
        return redirect('fittings:dashboard')

    fits = Fitting.objects.all()
    ships = Fitting.objects.order_by('ship_type').values('ship_type', 'ship_type__type_name')\
        .annotate(a=Count('ship_type'))
    ctx['fittings'] = fits
    ctx['ships'] = ships
    return render(request, 'fittings/add_doctrine.html', context=ctx)


@permission_required('fittings.access_fittings')
@login_required()
def view_doctrine(request, doctrine_id):
    ctx = {}
    try:
        doctrine = Doctrine.objects.prefetch_related('category')\
            .prefetch_related(Prefetch('fittings', Fitting.objects.select_related('ship_type')))\
            .prefetch_related('fittings__category')\
            .prefetch_related('fittings__doctrines')\
            .prefetch_related('fittings__doctrines__category').get(pk=doctrine_id)
    except Doctrine.DoesNotExist:
        messages.warning(request, 'Doctrine not found!')

        return redirect('fittings:dashboard')

    ctx['doctrine'] = doctrine
    ctx['d_cats'] = doctrine.category.all()
    ctx['fits'] = doctrine.fittings.all()

    # Build fit category list
    categories = dict()
    for fit in ctx['fits']:
        cats = []
        ids = []
        for cat in fit.category.all():
            if cat.pk not in ids:
                cats.append(cat)
                ids.append(cat.pk)
        for doc in fit.doctrines.all():
            for cat in doc.category.all():
                if cat.pk not in ids:
                    cats.append(cat)
                    ids.append(cat.pk)
        categories[fit.pk] = cats
    del ids
    ctx['f_cats'] = categories

    return render(request, 'fittings/view_doctrine.html', context=ctx)


@permission_required('fittings.access_fittings')
@login_required()
def view_all_fits(request):
    ctx = {}

    if request.user.has_perm('fittings.manage'):
        fits = Fitting.objects.prefetch_related('category', 'doctrines__category', 'ship_type').all()
    else:
        groups = request.user.groups.all()
        fits = Fitting.objects.prefetch_related('category', 'doctrines__category', 'ship_type').filter(
            Q(Q(category__groups__in=groups) |
              Q(category__isnull=True) |
              Q(category__groups__isnull=True)) &
            Q(Q(doctrines__category__groups__isnull=True) |
              Q(doctrines__category__groups__in=groups) |
              Q(doctrines__category__isnull=True)))
    ctx['fits'] = fits
    categories = dict()
    for fit in fits:
        cats = []
        ids = []
        for cat in fit.category.all():
            if cat.pk not in ids:
                cats.append(cat)
                ids.append(cat.pk)
        for doc in fit.doctrines.all():
            for cat in doc.category.all():
                if cat.pk not in ids:
                    cats.append(cat)
                    ids.append(cat.pk)
        categories[fit.pk] = cats
    ctx['cats'] = categories
    return render(request, 'fittings/view_all_fits.html', context=ctx)


@permission_required('fittings.manage')
@login_required()
def edit_doctrine(request, doctrine_id):
    ctx = {}
    try:
        doctrine = Doctrine.objects.get(pk=doctrine_id)
    except Doctrine.DoesNotExits:
        messages.warning(request, 'Doctrine not found!')

        return redirect('fittings:dashboard')

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        icon_url = request.POST['iconSelect']
        fitSelect = [int(fit) for fit in request.POST.getlist('fitSelect')]
        fits = doctrine.fittings.all()

        fits = Fitting.objects.filter(pk__in=fitSelect)
        doctrine.name = name
        doctrine.description = description
        doctrine.icon_url = icon_url
        doctrine.save()
        doctrine.fittings.clear()
        for fit in fitSelect:
            doctrine.fittings.add(fit)
        return redirect('fittings:view_doctrine', doctrine_id)

    ships = Fitting.objects.order_by('ship_type').values('ship_type', 'ship_type__type_name') \
        .annotate(a=Count('ship_type'))
    ctx['ships'] = ships
    ctx['doctrine'] = doctrine
    ctx['doc_fits'] = doctrine.fittings.all()
    ctx['fits'] = Fitting.objects.exclude(pk__in=ctx['doc_fits']).all()
    return render(request, 'fittings/edit_doctrine.html', context=ctx)


@permission_required('fittings.manage')
@login_required()
def delete_doctrine(request, doctrine_id):
    try:
        doctrine = Doctrine.objects.get(pk=doctrine_id)
    except Doctrine.DoesNotExist:
        messages.warning(request, 'Doctrine not found!')

        return redirect('fittings:dashboard')

    doctrine.delete()

    return redirect('fittings:dashboard')


@permission_required('fittings.manage')
@login_required()
def view_all_categories(request):
    ctx = {}
    cats = Category.objects\
        .all()\
        .annotate(groups_count=Count('groups', distinct=True))\
        .annotate(doctrines_count=Count('doctrines', distinct=True))\
        .annotate(fittings_count=Count('fittings', distinct=True))\
        .annotate(d_fittings_count=Count('doctrines__fittings', distinct=True))\
        .annotate(total_fits=F('fittings_count')+F('d_fittings_count'))
    for cat in cats:
        logger.debug(f'{cat.name}: Groups {cat.groups_count}')
    ctx['cats'] = cats
    return render(request, 'fittings/view_all_categories.html', context=ctx)


@permission_required('fittings.manage')
@login_required()
def add_category(request):
    ctx = {}
    if request.method == 'POST':
        logger.critical("POSTED")
        name = request.POST['name']
        color = request.POST['color']
        fitSelect = [int(fit) for fit in request.POST.getlist('fitSelect')]
        docSelect = [int(doc) for doc in request.POST.getlist('docSelect')]
        groupSelect = [int(grp) for grp in request.POST.getlist('groupSelect')]

        cat = Category(name=name, color=color)
        cat.save()
        for fit in fitSelect:
            cat.fittings.add(fit)
        for doc in docSelect:
            cat.doctrines.add(doc)
        for group in groupSelect:
            cat.groups.add(group)
        return redirect('fittings:view_category', cat.pk)
    fits = Fitting.objects.all()
    docs = Doctrine.objects.all()
    groups = Group.objects.all()

    ctx = {'groups': groups, 'fits': fits, 'docs': docs}
    return render(request, 'fittings/cat_form.html', ctx)


def view_category(request, cat_id):
    return redirect('fittings:dashboard')


def edit_category(request, cat_id):
    pass


@permission_required('fittings.manage')
@login_required()
def delete_fit(request, fit_id):
    try:
        fit = Fitting.objects.get(pk=fit_id)
    except Doctrine.DoesNotExist:
        messages.warning(request, 'Fit not found!')

        return redirect('fittings:dashboard')

    fit.delete()

    return redirect('fittings:dashboard')


@permission_required('fittings.access_fittings')
@login_required()
@token_required(scopes=('esi-fittings.write_fittings.v1',))
def save_fit(request, token, fit_id):
    try:
        fit = Fitting.objects.get(pk=fit_id)
    except Fitting.DoesNotExist:
        messages.warning(request, 'Fit not found!')

        return redirect('fitting:dashboard')

    access = _check_fit_access(request.user, fit_id)
    if not access:
        messages.warning(request, 'You do not have access to that fit.')

        return redirect('fittings:dashboard')

    # Build POST payload
    fit_dict = {
        'description': fit.description,
        'name': fit.name,
        'ship_type_id': fit.ship_type_type_id,
        'items': []
    }
    for item in fit.items.all():
        f_item = {
            'flag': item.flag,
            'quantity': item.quantity,
            'type_id': item.type_id
        }
        fit_dict['items'].append(f_item)

    # Get client
    c = esi.client
    fit = c.Fittings\
        .post_characters_character_id_fittings(character_id=token.character_id, fitting=fit_dict,
                                               token=token.valid_access_token()).result()

    return redirect('fittings:dashboard')
