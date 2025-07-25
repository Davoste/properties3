from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import NewsletterSubscriber, City, Property, BlogPost, PropertyType, PropertyImage, PropertyVideo, Country, ExchangeRate
from django.contrib.admin.views.decorators import staff_member_required
from .tasks import update_currency_rates
from .utils import convert_from_kes, convert_to_kes
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

# Create your views here.
def home(request):
    properties = Property.objects.filter(is_featured=True)  
    return render(request, 'core/home.html',{'properties': properties})



def set_currency(request):
    currency = request.GET.get("currency", "KES")
    response = redirect(request.META.get("HTTP_REFERER", "/"))
    response.set_cookie("currency", currency)
    return response


@staff_member_required
def update_exchange_rates_view(request):
    update_currency_rates.delay()  # Run as a background task (celery + redis + beat scheduler)
    return JsonResponse({"message": "Exchange rate update triggered."})

def blog(request):
    blogs = BlogPost.objects.all().order_by('published_at')  # Adjust ordering as needed
    return render(request, 'core/blogs.html', {'blogs': blogs})

def about(request):
    return render(request, 'core/about.html')

# def blog(request):
#     return render(request, 'core/blogs.html')

def blog_details(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'core/blog_detail.html', {'blog': blog})

def contact(request):
    return render(request, 'core/contact.html')

def invest(request):
    return render(request, 'core/invest.html')

def get_featured_properties(request):
    # Get user specific currency if any (default to KES)
    currency = request.COOKIES.get("currency", "KES")

    # Get featured poperties
    featured_properties_list = Property.objects.filter(is_published=True, is_featured=True).select_related(
        'city', 'city__country', 'property_type', 'featured_image'
    ).order_by('-listed_date')
    paginator = Paginator(featured_properties_list, 4)

    try:
        page_number = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page_number = 1

    print(f"this is the page number: {page_number}")    


    try:
        featured_properties = paginator.page(page_number)

    except PageNotAnInteger:
        featured_properties = paginator.page(1)

    except EmptyPage:
        featured_properties = paginator.page(paginator.num_pages)        

    property_data = []
    for prop in featured_properties:
        converted_price = convert_from_kes(prop.price, currency)

        property_data.append({
            "id": prop.id,
            "title": prop.title,
            "description": prop.description,
            "purpose": prop.purpose,
            "property_type": prop.property_type.name,
            "price": float(converted_price),  
            "currency": currency,             # Add currency label
            "address": prop.address,
            "bedrooms": prop.bedrooms,
            "sqft": prop.sqft,
            "lot_size": prop.lot_size,
            "country": prop.city.country.name,
            "city": prop.city.name,
            "image": prop.featured_image.image.url if prop.featured_image else None,
            "image_alt_text": prop.featured_image.alt_text if prop.featured_image else "Property Image",
        })

    return JsonResponse({
        'properties': property_data,
        'current_page': featured_properties.number,
        'has_next': featured_properties.has_next(),
        'has_prev': featured_properties.has_previous(),
    }, safe=False)


def get_countries(request):
    # Get countries with at least one property
    country_list = Country.objects.annotate(
        property_count=Count('city__properties')
    ).filter(property_count__gt=0).order_by('-property_count')

    paginator = Paginator(country_list, 10) 
    page_number = request.GET.get('page')

    try:
        countries = paginator.page(page_number)
    except PageNotAnInteger:
        countries = paginator.page(1)
    except EmptyPage:
        countries = paginator.page(paginator.num_pages)

    country_data = [{
        'id': country.id,
        'name': country.name,
        'code': country.code,
        'currency_code': country.currency_code,
        'property_count': country.property_count,
        'flag_image': country.flag_image.url if country.flag_image else None,
        'flag_alt_text': country.flag_image.alt_text if country.flag_image and hasattr(country.flag_image, 'alt_text') else f"Flag of {country.name}"
    } for country in countries]

    return JsonResponse({
        'countries': country_data,
        'current_page': countries.number,
        'has_next': countries.has_next(),
        'has_prev': countries.has_previous(),
    }, safe=False)


def get_cities(request):
    # Get unique cities with top properties
    city_list = City.objects.annotate(property_count=Count('properties')).order_by('-property_count')

    paginator = Paginator(city_list, 10)

    page_number = request.GET.get('page')
    
    try:

        cities = paginator.page(page_number)

    except PageNotAnInteger:
        cities = paginator.page(1)

    except EmptyPage:
        cities = paginator.page(paginator.num_pages)

    city_data = [{
        'id': city.id,
        'name': city.name,
        'image': city.image.url if city.image else None,
        'image_alt_text': city.alt_text if city.alt_text else f"{city.name} image",
    }for city in cities]

    return JsonResponse({
        'cities': city_data,
        'current_page': cities.number,
        'has_next': cities.has_next(),
        'has_prev': cities.has_previous(),
    }, safe=False)

def get_property_types(request):
    property_types = PropertyType.objects.all()

    property_type_list = [{
        'property_type': property_type.name,
        'property_type_image': property_type.image.url if property_type.image else None,
        'property_type_image_alt_text': property_type.alt_text if property_type.alt_text else f"property {property_type.name} image",
    }for property_type in property_types]

    return JsonResponse({
        'property_types': property_type_list
    }, safe=False)




def properties(request):
    if request.method == 'GET':
        # Get all published properties
        properties_qs = Property.objects.filter(is_published=True).select_related('city', 'city__country', 'property_type', 'featured_image')
        property_types = PropertyType.objects.all()
        countries = Country.objects.all()
        cities = City.objects.all()

        # Filters
        purpose = request.GET.get('purpose')
        prop_type = request.GET.get('property_type')
        price_min = request.GET.get('price_min')
        price_max = request.GET.get('price_max')
        bedrooms = request.GET.get('bedrooms')
        bathrooms = request.GET.get('bathrooms')
        sqft = request.GET.get('sqft')
        country = request.GET.get('country')
        city = request.GET.get('city')

        if purpose:
            properties_qs = properties_qs.filter(purpose=purpose)
        if prop_type:
            properties_qs = properties_qs.filter(property_type_id=prop_type)
        if price_min:
            properties_qs = properties_qs.filter(price__gte=price_min)
        if price_max:
            properties_qs = properties_qs.filter(price__lte=price_max)
        if bedrooms:
            properties_qs = properties_qs.filter(bedrooms=bedrooms)
        if bathrooms:
            properties_qs = properties_qs.filter(bathrooms=bathrooms)
        if sqft:
            properties_qs = properties_qs.filter(sqft__gte=sqft)
        if city:
            properties_qs = properties_qs.filter(city_id=city)
        elif country:
            properties_qs = properties_qs.filter(city__country_id=country)

        # Paginate properties
        paginator = Paginator(properties_qs, 8)
        page = request.GET.get('page')
        properties_page = paginator.get_page(page)

        context = {
            'property_types': property_types,
            'countries': countries,
            'cities': cities,
            'properties': properties_page,
        }

        return render(request, 'core/properties.html', context)

    else:
        # Handle POST if needed later
        return redirect('core:properties')


def get_property_details(request, id):
    property = Property.objects.get(id=id)
    context = {
        'property': property
    }
    return render(request, 'core/property_detail.html', context)

def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full-name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        reason = request.POST.get('reason')
        message = request.POST.get('message')

        # Compose email content
        subject = f"Contact Form Submission: {reason.title()}"
        content = f"""
        You have a new contact form submission:

        Full Name: {full_name}
        Email: {email}
        Phone: {phone}
        Reason for Contact: {reason}
        Message: {message}
        """

        # Send email
        send_mail(
            subject,
            content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],  # or your company's contact email
            fail_silently=False,
        )

        messages.success(request, 'Your message has been sent successfully. We will get back to you shortly.')
        return redirect('core:contact')

    return render(request, 'core/contact.html')

def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, "You have successfully subscribed to our newsletter!")
            else:
                messages.info(request, "You are already subscribed to our newsletter.")
        else:
            messages.error(request, "Please enter a valid email address.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
