# Generated by Django 5.2.1 on 2025-06-03 07:45

import django.db.models.deletion
import django_ckeditor_5.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=2, unique=True)),
                ('currency_code', models.CharField(default='KES', max_length=3)),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_currency', models.CharField(help_text='Currency code like USD, EUR, GBP, JPY', max_length=3, unique=True)),
                ('rate_from_kes', models.DecimalField(decimal_places=6, max_digits=12)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('content', django_ckeditor_5.fields.CKEditor5Field()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('subscription_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('website', models.URLField(blank=True)),
                ('logo', models.ImageField(upload_to='partners/')),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(default='default_property_type.jpg', upload_to='property_type_images/')),
            ],
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('content', django_ckeditor_5.fields.CKEditor5Field()),
                ('published', models.BooleanField(default=False)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(default='default_images/default_city.jpg', upload_to='city_images/')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.country')),
            ],
            options={
                'verbose_name_plural': 'Cities',
                'unique_together': {('name', 'country')},
            },
        ),
        migrations.CreateModel(
            name='NewsletterDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='core.newsletter')),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.newslettersubscriber')),
            ],
            options={
                'verbose_name_plural': 'Newsletter deliveries',
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('purpose', models.CharField(choices=[('Rent', 'Rent'), ('Sale', 'Sale')], max_length=4)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('address', models.CharField(max_length=255)),
                ('zipcode', models.CharField(max_length=20)),
                ('bedrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('bathrooms', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('sqft', models.PositiveIntegerField(blank=True, null=True)),
                ('lot_size', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('listed_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='properties', to='core.city')),
            ],
            options={
                'verbose_name_plural': 'Properties',
            },
        ),
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('interest', models.CharField(blank=True, choices=[('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Land', 'Land/Plots'), ('Rental', 'Rental Property')], max_length=20, null=True)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('responded', models.BooleanField(default=False)),
                ('response', models.TextField(blank=True, null=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inquiries', to='core.property')),
            ],
            options={
                'verbose_name_plural': 'Inquiries',
            },
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='property_images/')),
                ('alt_text', models.CharField(blank=True, max_length=255)),
                ('is_primary', models.BooleanField(default=False, help_text='Automatically set as property thumbnail')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.property')),
            ],
            options={
                'ordering': ['property', '-is_primary', 'id'],
            },
        ),
        migrations.AddField(
            model_name='property',
            name='featured_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='featured_for_property', to='core.propertyimage'),
        ),
        migrations.AddField(
            model_name='property',
            name='property_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.propertytype'),
        ),
        migrations.CreateModel(
            name='PropertyVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_url', models.URLField(help_text='YouTube or Vimeo URL')),
                ('caption', models.CharField(blank=True, max_length=255)),
                ('is_featured', models.BooleanField(default=False, help_text='Feature this video as the main tour')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='core.property')),
            ],
            options={
                'ordering': ['property', 'is_featured', '-created_at'],
            },
        ),
    ]
