from django.urls import path
from . import views

urlpatterns = [
    # Inicio
    path("", views.InicioView.as_view(), name="inicio"),
    path("perfil/", views.PerfilView.as_view(), name="perfil"),

    # Libros
    path("libros/", views.LibroListView.as_view(), name="lista_libros"),
    path("libros/nuevo/", views.LibroCreateView.as_view(), name="crear_libro"),
    path("libros/<int:pk>/", views.LibroDetailView.as_view(), name="detalle_libro"),
    path("libros/<int:pk>/comentario/nuevo/", views.ComentarioCreateView.as_view(), name="crear_comentario"),
    path("libros/<int:pk>/editar/", views.LibroUpdateView.as_view(), name="editar_libro"),
    path("libros/<int:pk>/eliminar/", views.LibroDeleteView.as_view(), name="eliminar_libro"),
    path("libros/<int:pk>/alquilar/", views.alquilar_libro, name="alquilar_libro"),
    path("alquiler/<int:pk>/devolver/", views.devolver_alquiler, name="devolver_alquiler"),

    # Autores
    path("autores/", views.AutorListCreateView.as_view(), name="lista_autores"),
    path("autores/<int:pk>/", views.AutorDetailView.as_view(), name="detalle_autor"),

    # Editoriales
    path("editoriales/", views.EditorialListCreateView.as_view(), name="lista_editoriales"),
    path("editoriales/<int:pk>/", views.EditorialDetailView.as_view(), name="detalle_editorial"),
]