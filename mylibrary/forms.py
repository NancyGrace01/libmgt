from django import forms
from .models import Book, Category, Profile

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category']

    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Title:', 'class': 'form-control'}),
        label="Title"
    )
    author = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Author:', 'class': 'form-control'}),
        label="Author"
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'placeholder': 'Category:', 'class': 'form-control'}),
        label="Category"
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'})
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'state', 'city', 'gender', 'occupation', 'profile_picture']