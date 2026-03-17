from django.contrib import admin
from .models import Autor, Editorial, Libro, Comentario, Alquiler


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais')
    search_fields = ('nombre',)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'editorial', 'fecha_publicacion')
    list_filter = ('editorial', 'autor')
    search_fields = ('titulo',)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'libro', 'creado')
    list_filter = ('libro', 'autor')
    search_fields = ('texto',)

@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'fecha_inicio', 'fecha_devolucion_prevista', 'estado')
    list_filter = ('estado',)