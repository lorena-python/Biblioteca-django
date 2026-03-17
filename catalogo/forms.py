from django import forms
from .models import Libro, Autor, Editorial, Comentario


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'editorial', 'sinopsis', 'fecha_publicacion', 'portada']
        widgets = {
            'fecha_publicacion': forms.DateInput(attrs={'type': 'date'}),
        }

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre']     

class EditorialForm(forms.ModelForm):
    class Meta:
        model = Editorial
        fields = ['nombre']

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["texto"]  