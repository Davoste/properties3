from django import forms
from .models import Property, PropertyImage, BlogPost


# PROPERTY FORM
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'purpose', 'property_type',
            'price', 'address', 'Country', 'city', 'zipcode',
            'bedrooms', 'bathrooms', 'sqft', 'lot_size', 'is_published'
        ]
        labels = {
            'title': 'Property Title',
            'description': 'Description',
            'purpose': 'For Rent or Sale?',
            'property_type': 'Type of Property',
            'price': 'Price',
            'address': 'Address',
            'Country': 'Country',
            'city': 'City',
            'zipcode': 'ZIP Code',
            'bedrooms': 'Number of Bedrooms',
            'bathrooms': 'Number of Bathrooms (e.g., 1.5)',
            'sqft': 'Square Feet (Interior Space)',
            'lot_size': 'Lot Size (in acres or sqft)',
            'is_published': 'Publish Property?'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'Country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# PROPERTY IMAGE FORM
class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'alt_text']
        labels = {
            'image': 'Upload Image',
            'alt_text': 'Alternative Text (for accessibility)'
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }



# BLOG POST FORM
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'content', 'published']
        labels = {
            'title': 'Blog Post Title',
            'slug': 'URL Slug',
            'content': 'Content',
            'published': 'Publish Now?'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }




