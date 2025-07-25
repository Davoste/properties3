from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
# Partners Model
from django.db import models

class Partner(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='partners/')
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)  # For display control
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)  # ISO country code: 'KE', 'US'
    currency_code = models.CharField(max_length=3, default='KES')  # ISO 4217: 'KES', 'USD', 'EUR'
    flag_image = models.ImageField(upload_to='country_flag_images/', default='default_images/default_country_flag.jpg/')

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='city_images/', default='default_images/default_city.jpg')
    alt_text = models.CharField(max_length=255, blank=True)
    class Meta:
        unique_together = ('name', 'country')
        verbose_name_plural = 'Cities'

    def __str__(self):
        return f"{self.name}"

class PropertyType(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='property_type_images/', default='default_property_type.jpg')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

# Property Model
class Property(models.Model):


    PROPERTY_CATEGORY = [
        ('Rent', 'Rent'),
        ('Sale', 'Sale'),
    ]


    featured_image = models.ForeignKey(
        'PropertyImage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_for_property'
    )
    title = models.CharField(max_length=255)
    is_featured = models.BooleanField(default=False)
    description = models.TextField()
    purpose = models.CharField(max_length=4, choices=PROPERTY_CATEGORY)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='properties')
    zipcode = models.CharField(max_length=20)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # e.g., 1.5 baths
    sqft = models.PositiveIntegerField(null=True, blank=True)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in acres or sqft
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    listed_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Properties'

# Property Images
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Automatically set as property thumbnail")

    class Meta:
        ordering = ['property', '-is_primary', 'id']  

    def save(self, *args, **kwargs):
        # If marking as primary, unset others
        if self.is_primary:
            PropertyImage.objects.filter(property=self.property) \
                                .exclude(pk=self.pk) \
                                .update(is_primary=False)
        super().save(*args, **kwargs)


# Property Videos
class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video_url = models.URLField(help_text="YouTube or Vimeo URL")
    caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Feature this video as the main tour")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['property', 'is_featured', '-created_at']

    def __str__(self):
        return f"Video for {self.property.title}"



@receiver(post_save, sender=PropertyImage)
def set_property_thumbnail(sender, instance, created, **kwargs):
    """
    Automatically set property.featured_image when:
    1. First image is uploaded
    2. An image is explicitly marked as primary
    """
    property = instance.property

    if not property.featured_image or instance.is_primary:
        property.featured_image = instance
        property.save()



# Exchange Rates from "currency" TO KES_
class ExchangeRate(models.Model):
    target_currency = models.CharField(
        max_length=3,
        unique=True,
        help_text="Currency code like USD, EUR, GBP, JPY"
    )
    kes_to_currency = models.DecimalField(
        max_digits=12,
        decimal_places=6,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"1 KES = {self.rate_from_kes} {self.target_currency} (Updated: {self.updated_at})"


# Messages (inquiries) sent by users, admin can respond
class Inquiry(models.Model):
    INTEREST_CHOICES = (
        ('Residential', 'Residential'),
        ('Commercial', 'Commercial'),
        ('Land', 'Land/Plots'),
        ('Rental', 'Rental Property'),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    interest = models.CharField(
        max_length=20,
        choices=INTEREST_CHOICES,
        blank=True,
        null=True
    )
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    # Admin Response Fields
    responded = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Inquiry from {self.name} about {self.property}"
    
    class Meta:
        verbose_name_plural = 'Inquiries'


# Blog Post Model
class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # usually admin users
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    content = CKEditor5Field()
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']



class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscription_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    title = models.CharField(max_length=50)
    content = CKEditor5Field()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title
    

class NewsletterDelivery(models.Model):
    subscriber = models.ForeignKey(NewsletterSubscriber, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='deliveries')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Newsletter deliveries"

    def __str__(self):
        return f"{self.newsletter.title} sent to {self.subscriber.email}"



