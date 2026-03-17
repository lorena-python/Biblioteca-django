from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin

from .models import Libro, Autor, Editorial, Comentario, Alquiler
from .forms import LibroForm, AutorForm, EditorialForm, ComentarioForm


# INICIO
class InicioView(TemplateView):
    template_name = "catalogo/inicio.html"


# LIBROS 
class LibroListView(LoginRequiredMixin, ListView):
    model = Libro
    template_name = "catalogo/libro_list.html"
    context_object_name = "libros"
    paginate_by = 5

    def get_queryset(self):
        qs = Libro.objects.all().order_by("titulo")
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(titulo__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()

        # Libros NO disponibles (tienen un alquiler ACTIVO o ATRASADO sin devolución real)
        no_disponibles = set(
            Alquiler.objects.filter(
                fecha_devolucion_real__isnull=True,
                estado__in=["ACTIVO", "ATRASADO"],
            ).values_list("libro_id", flat=True)
        )
        context["no_disponibles"] = no_disponibles
        return context

# DETALLE LIBRO
class LibroDetailView(LoginRequiredMixin,DetailView):
    model = Libro
    template_name = "catalogo/libro_detail.html"
    context_object_name = "libro"

class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm
    template_name = "catalogo/comentario_form.html"

    def form_valid(self, form):
        # Asigna el usuario autenticado sí o sí (no manipulable)
        form.instance.autor = self.request.user

        # Vincula el comentario al libro por la URL
        libro = Libro.objects.get(pk=self.kwargs["pk"])
        form.instance.libro = libro

        return super().form_valid(form)

    def get_success_url(self):
        # Volver al detalle del libro
        return reverse("detalle_libro", kwargs={"pk": self.kwargs["pk"]})

# CREAR LIBRO
class LibroCreateView(CreateView):
    model = Libro
    form_class = LibroForm
    template_name = "catalogo/libro_form.html"
    success_url = reverse_lazy("lista_libros")


# EDITAR LIBRO
class LibroUpdateView(UpdateView):
    model = Libro
    form_class = LibroForm
    template_name = "catalogo/libro_form.html"

    def get_success_url(self):
        return reverse("detalle_libro", kwargs={"pk": self.object.pk})


# ELIMINAR LIBRO
class LibroDeleteView(DeleteView):
    model = Libro
    template_name = "catalogo/libro_confirm_delete.html"
    success_url = reverse_lazy("lista_libros")


# AUTORES (lista + crear en la misma vista)
class AutorListCreateView(FormMixin, ListView):
    model = Autor
    template_name = "catalogo/autor_list.html"
    context_object_name = "autores"
    form_class = AutorForm
    success_url = reverse_lazy("lista_autores")

    def get_queryset(self):
        return Autor.objects.all().order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        # si hay errores, volvemos a renderizar la lista + form con errores
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class AutorDetailView(DetailView):
    model = Autor
    template_name = "catalogo/autor_detalle.html"
    context_object_name = "autor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["libros"] = Libro.objects.filter(autor=self.object).order_by("titulo")
        return context


# EDITORIALES (lista + crear en la misma vista)
class EditorialListCreateView(FormMixin, ListView):
    model = Editorial
    template_name = "catalogo/editorial_list.html"
    context_object_name = "editoriales"
    form_class = EditorialForm
    success_url = reverse_lazy("lista_editoriales")

    def get_queryset(self):
        return Editorial.objects.all().order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class EditorialDetailView(DetailView):
    model = Editorial
    template_name = "catalogo/editorial_detalle.html"
    context_object_name = "editorial"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["libros"] = Libro.objects.filter(editorial=self.object).order_by("titulo")
        return context

@login_required
def alquilar_libro(request, pk):
    if request.method != "POST":
        return redirect("lista_libros")

    libro = get_object_or_404(Libro, pk=pk)

    try:
        alquiler = Alquiler(
            usuario=request.user,
            libro=libro,
            fecha_inicio=timezone.now().date(),
            fecha_devolucion_prevista=timezone.now().date() + timedelta(days=3),
            estado="ACTIVO",
        )

        alquiler.full_clean()
        alquiler.save()

        messages.success(request, f"Alquiler registrado: {libro.titulo}")

    except ValidationError as e:
        messages.error(request, e.messages[0])

    except Exception:
        messages.error(request, "No se pudo crear el alquiler.")

    return redirect("lista_libros")

@login_required
def devolver_alquiler(request, pk):
    if request.method != "POST":
        return redirect("perfil")

    alquiler = get_object_or_404(Alquiler, pk=pk, usuario=request.user)

    # Seguridad: no devolver si no está activo
    if alquiler.estado != "ACTIVO":
        messages.error(request, "Este libro no está actualmente alquilado.")
        return redirect("perfil")

    alquiler.fecha_devolucion_real = timezone.now().date()
    alquiler.estado = "DEVUELTO"
    alquiler.save()

    messages.success(request, f"Libro devuelto: {alquiler.libro.titulo}")
    return redirect("perfil") 

class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = "catalogo/perfil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Usuario autenticado
        user = self.request.user
        context["usuario"] = user

        # Alquileres activos del usuario
        context["alquileres_activos"] = (
            Alquiler.objects
            .filter(usuario=user, estado="ACTIVO")
            .select_related("libro")
            .order_by("-fecha_inicio")
        )

        return context 