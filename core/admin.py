from django.contrib import admin
from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.utils.html import format_html, mark_safe
from django.utils.http import urlencode
from django.urls import reverse, path
from .models import NewsletterSubscriber,Partner, Property, PropertyImage, PropertyVideo, ExchangeRate, Inquiry, BlogPost, Newsletter, NewsletterDelivery, NewsletterSubscriber, City, Country, PropertyType
from django.shortcuts import redirect

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.core.mail import send_mail

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule
from django_celery_beat.admin import PeriodicTaskAdmin, IntervalScheduleAdmin, CrontabScheduleAdmin, SolarScheduleAdmin, ClockedScheduleAdmin

# Custom Admin Site
class SevenFlagsAdminSite(admin.AdminSite):
    site_header = "Seven Flags Real Estate Admin"
    site_title = "Seven Flags Dashboard"
    index_title = "Welcome to Seven Flags Admin"
    
    def each_context(self, request):
        context = super().each_context(request)
        # Apply custom colors
        context['site_header_color'] = '#000000'  # Black
        context['primary_color'] = '#B8860B'      # Gold
        context['secondary_color'] = '#42586488'   # Dark Blue with transparency
        context['unresponded_inquiries_count'] = Inquiry.objects.filter(responded=False).count()
        return context
    
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        # Add badge to the Inquiries model
        for app in app_list:
            if app['app_label'] == 'core':  
                for model in app['models']:
                    if model['object_name'] == 'Inquiry':
                        count = Inquiry.objects.filter(responded=False).count()
                        if count > 0:
                            model['name'] = format_html(
                                '{} <span class="unresponded-badge" style="color: #fff; background: #4CAF50; border-radius: 100%; border: none; padding:0.4px 3.4px; font-size: 9px; margin-left: 4px; ">{}</span>',
                                model['name'],
                                count
                            )
        return app_list

admin_site = SevenFlagsAdminSite(name='sevenflags_admin')

# Custom CSS for admin
class CustomAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

# Partner Admin
@admin.register(Partner, site=admin_site)
class PartnerAdmin(CustomAdmin):
    list_display = ('name', 'website_link', 'logo_preview', 'active')
    list_editable = ('active',)
    search_fields = ('name',)
    search_help_text = "Search by: name"
    list_filter = ('name', 'active')
    
    def website_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website) if obj.website else "-"
    website_link.short_description = "Website"
    
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-height: 50px;" />')
        return "No Image"
    logo_preview.short_description = "Logo Preview"

# Inline for Property Images
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3
    fields = ('image_preview', 'image', 'alt_text', 'is_primary')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 80px;" />')
        return "No Image"
    image_preview.short_description = "Preview"

# Inline for Property Videos
class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 1
    fields = ('video_url', 'caption', 'is_featured')
    verbose_name = "Property Video"
    verbose_name_plural = "Property Videos"

@admin.register(PropertyType, site=admin_site)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'has_image', 'alt_text_preview', 'image_preview')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    readonly_fields = ('has_image', 'image_preview')
    fields = ('name', 'slug', 'description', 'image', 'alt_text')

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = 'Has Image'

    def alt_text_preview(self, obj):
        return obj.alt_text or "-"

    alt_text_preview.short_description = 'Alt Text'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.image.url)
        return "-"

    image_preview.short_description = 'Image Preview'

# Property Admin
@admin.register(Property, site=admin_site)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline, PropertyVideoInline]
    list_display = ('title', 'admin_thumbnail', 'purpose', 'property_type', 'price', 'get_country', 'city', 'is_published', 'created_short', 'is_featured', 'view_count')
    list_editable = ('is_published', 'is_featured')
    list_filter = ('is_featured','purpose', 'property_type' , 'city__country', 'city', 'is_published', 'is_featured', 'view_count')
    list_per_page = 5
    list_max_show_all = 1000
    search_fields = ('title', 'address', 'city', 'city__country')
    search_help_text = "Search by: title | country | city | address e.g Kitengela"
    readonly_fields = ('created_short',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'purpose', 'property_type', 'view_count')
        }),
        ('Location', {
            'fields': ('address', 'city', 'zipcode')
        }),
        ('Details', {
            'fields': ('price', 'bedrooms', 'bathrooms', 'sqft', 'lot_size')
        }),
        ('Status', {
            'fields': ('is_published', 'created_short', 'is_featured')
        }),
    )

    @admin.display(description='Country')
    def get_country(self, obj):
        return obj.city.country.name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('city__country')

    def get_ordering(self, request):
        return ['city__country__name']

    def admin_thumbnail(self, obj):
        if obj.featured_image:
            return mark_safe(
                f'<img src="{obj.featured_image.image.url}" '
                f'style="max-height: 100px; max-width: 160px; '
                f'object-fit: cover; border-radius: 8px;" />'
            )
        return "No Image"
    admin_thumbnail.short_description = "Thumbnail"
    
    def created_short(self, obj):
        return obj.listed_date.strftime("%b %d, %Y")
    created_short.short_description = "Listed Date"

    



# Exchange Rate Admin
@admin.register(ExchangeRate, site=admin_site)
class ExchangeRateAdmin(CustomAdmin):
    list_display = ('target_currency', 'kes_to_currency', 'updated_short')
    list_editable = ('kes_to_currency',)
    search_fields = ('target_currency',)
    
    def updated_short(self, obj):
        return obj.updated_at.strftime("%b %d, %Y")
    updated_short.short_description = "Last Updated"

    # Disable add permission
    def has_add_permission(self, request):
        return False  # Hides the "+Add" button

# Inquiry Admin
@admin.register(Inquiry, site=admin_site)
class InquiryAdmin(CustomAdmin):
    list_display = ('name', 'email', 'property_link', 'interest', 'responded', 'sent_short')
    list_filter = ('interest', 'responded', 'property__title')
    
    search_fields = ('name', 'email', 'property__title')
    search_help_text = "Search by: property title | name | email"
    readonly_fields = ('responded','name', 'email', 'phone', 'interest', 'subject', 'message')
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('property', 'name', 'email', 'phone', 'interest', 'subject', 'message')
        }),
        ('Response', {
            'fields': ('responded', 'response', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def property_link(self, obj):
        if obj.property:
            url = reverse('admin:core_property_change', args=[obj.property.id])
            return format_html('<a href="{}">{}</a>', url, obj.property.title)
        return "-"
    property_link.short_description = "Property"
    
    def sent_short(self, obj):
        return obj.sent_at.strftime("%b %d, %Y")
    sent_short.short_description = "Sent Date"


    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property')
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['unresponded_count'] = Inquiry.objects.filter(responded=False).count()
        extra_context['title'] = 'Select inquiry to respond to'
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_list_display_links(self, request, list_display):
        # Make the badge clickable
        return ['status_badge'] + super().get_list_display_links(request, list_display)

        
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['unresponded_count'] = Inquiry.objects.filter(responded=False).count()
        return perms
    
    # Disable add permission
    def has_add_permission(self, request):
        return False  # Hides the "+Add" button
    


# Blog Post Admin
@admin.register(BlogPost, site=admin_site)
class BlogPostAdmin(CustomAdmin):
    list_display = ('title', 'author', 'published', 'published_short')
    list_filter = ('published', 'title', 'author')
    list_editable = ('published',)
    search_fields = ('title', 'content')
    search_help_text = "Search by: title | content"
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    
    def published_short(self, obj):
        if obj.published_at:
            return obj.published_at.strftime("%b %d, %Y")
        return "Not Published"
    published_short.short_description = "Publish Date"

# Register PropertyImage and PropertyVideo separately
@admin.register(PropertyImage, site=admin_site)
class PropertyImageAdmin(CustomAdmin):
    list_display = ('property', 'image_preview', 'alt_text', 'is_primary')
    
    list_filter = ('property__title', 'property__purpose')  # Filter by property fields
    search_help_text = "Search by: Property Title | Address | City"
    search_fields = (
        'property__title',  # Search by property title
        'property__address',  # Search by property address
        'property__city',  # Search by city
        
    )
    raw_id_fields = ('property',)  # Better for performance with many properties
    list_select_related = ('property',)  # Optimizes database queries
    actions = ['make_primary']
    # readonly_fields = ('is_primary',)

    # Customize the search placeholder
    def get_search_fields(self, request):
        search_fields = super().get_search_fields(request)
        self.search_fields_placeholder = "e.g. 'Nairobi', 'Beach House', '123 Main St'"
        return search_fields


    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 80px;" />')
        return "No Image"
    image_preview.short_description = "Preview"

    def make_primary(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one image", level='ERROR')
            return
        
        image = queryset.first()
        image.is_primary = True
        image.save()
        self.message_user(request, f"Set {image} as primary image")



@admin.register(PropertyVideo, site=admin_site)
class PropertyVideoAdmin(CustomAdmin):
    list_display = ('property', 'video_url', 'is_featured')
    raw_id_fields = ('property',)
    list_filter = ('property__title', 'is_featured',)
    search_fields = ('property__title',)
    search_help_text = "Search by: Property title "


@admin.register(Country, site=admin_site)
class CountryAdmin(CustomAdmin):
    list_display = ('name', 'code', 'currency_code', 'has_flag_image', 'flag_preview')
    search_fields = ('name', 'code', 'currency_code')
    search_help_text = "Search by: name | code | currency_code   e.g KE"
    readonly_fields = ('has_flag_image',)
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'currency_code')
        }),
        ('Flag Image', {
            'fields': ('flag_image', 'has_flag_image',)
        }),
    )

    def has_flag_image(self, obj):
        if obj.flag_image:
            return True
        return False
    has_flag_image.boolean = True
    has_flag_image.short_description = 'Has Flag Image'

    def flag_preview(self, obj):
        if obj.flag_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />'.format(obj.flag_image.url))
        return "-"
    flag_preview.short_description = 'Flag Preview'


@admin.register(City, site=admin_site)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_name', 'has_image', 'image_preview')
    search_fields = ('name', 'country__name')
    list_filter = ('country',)
    search_help_text = "Search by: city name | country e.g Kitengela"

    fieldsets = (
        (None, {
            'fields': ('name', 'country')
        }),
        ('Image', {
            'fields': ('image', 'alt_text')
        }),
    )

    def country_name(self, obj):
        return obj.country.name
    country_name.admin_order_field = 'country'
    country_name.short_description = 'Country'

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 80px;" />')
        return "No Image"
    image_preview.short_description = "Preview"


# @admin.register(NewsletterSubscriber, site=admin_site)
# class NewsletterSubscriberAdmin(admin.ModelAdmin):
#     list_display = ('email', 'subscription_date')
#     search_fields = ('email',)
#     readonly_fields = ('subscription_date',)
#     ordering = ('-subscription_date',)


@admin.register(NewsletterDelivery, site=admin_site)
class NewsletterDeliveryAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'newsletter', 'sent_at')
    list_filter = ('newsletter', 'subscriber')
    search_fields = ('subscriber__email', 'newsletter__title')
    readonly_fields = ('sent_at',)
    autocomplete_fields = ['subscriber', 'newsletter']

    # Disable add permission
    def has_add_permission(self, request):
        return False  # Hides the "+Add" button

# @admin.register(NewsletterSubscriber)
# class NewsletterSubscriberAdmin(admin.ModelAdmin):
#     list_display = ('email', 'subscription_date')
#     search_fields = ('email',)

@admin.register(NewsletterSubscriber, site=admin_site)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscription_date')
    search_fields = ('email',)
    readonly_fields = ('subscription_date',)
    ordering = ('-subscription_date',)
    actions = ['redirect_to_newsletter']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-newsletter/', self.admin_site.admin_view(self.send_newsletter_view), name='send_newsletter'),
        ]
        return custom_urls + urls

    def redirect_to_newsletter(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        return redirect(f"send-newsletter/?ids={','.join(str(pk) for pk in selected)}")

    redirect_to_newsletter.short_description = "Send custom newsletter to selected subscribers"

    def send_newsletter_view(self, request):
        from django.shortcuts import render
        from django.core.mail import send_mail
        from django.conf import settings

        ids = request.GET.get('ids')
        if not ids:
            self.message_user(request, "No subscribers selected.", level=messages.WARNING)
            return redirect('..')

        subscriber_ids = ids.split(',')
        subscribers = NewsletterSubscriber.objects.filter(pk__in=subscriber_ids)

        if request.method == "POST":
            subject = request.POST['subject']
            message = request.POST['message']
            recipient_list = subscribers.values_list('email', flat=True)

            if recipient_list:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                self.message_user(request, f"Newsletter sent to {len(recipient_list)} subscribers.", level=messages.SUCCESS)
                return redirect('..')
            else:
                self.message_user(request, "No valid recipients found.", level=messages.WARNING)
                return redirect('..')

        context = {
            'subscribers': subscribers,
            'ids': ids,
        }
        return render(request, 'admin/send_newsletter.html', context)
    
@admin.register(Newsletter, site=admin_site)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'get_subscribers_count')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    change_form_template = 'admin/change_form.html'  # Uses our custom template

    @admin.display(description='Subscribers Count')
    def get_subscribers_count(self, obj):
        return obj.deliveries.count()    
    


# Register Auth models
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

# Register Celery Beat models
admin_site.register(IntervalSchedule, IntervalScheduleAdmin)
admin_site.register(CrontabSchedule, CrontabScheduleAdmin)
admin_site.register(SolarSchedule, SolarScheduleAdmin)
admin_site.register(ClockedSchedule, ClockedScheduleAdmin)
admin_site.register(PeriodicTask, PeriodicTaskAdmin)    