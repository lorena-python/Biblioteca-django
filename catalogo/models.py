from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class Autor(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    biografia = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Editorial(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique= True, blank=True)
    pais = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros')
    editorial = models.ForeignKey(
        Editorial,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='libros'
    )
    sinopsis = models.TextField()
    fecha_publicacion = models.DateField()
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    texto = models.TextField()

    # Mantenemos relación con el "post" correspondiente (Libro)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="comentarios")

    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comentarios")

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario {self.id} en {self.libro}"

class Alquiler(models.Model):
    ESTADOS = (
        ("ACTIVO", "Activo"),
        ("DEVUELTO", "Devuelto"),
        ("ATRASADO", "Atrasado"),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alquileres"
    )
    libro = models.ForeignKey(
        "catalogo.Libro",
        on_delete=models.CASCADE,
        related_name="alquileres"
    )

    fecha_inicio = models.DateField(default=timezone.localdate)
    fecha_devolucion_prevista = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)

    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")

    def __str__(self):
        return f"{self.usuario} - {self.libro} ({self.estado})"

    def clean(self):
        # Si no hay libro aún, no validamos
        if not self.libro_id:
            return

        # Un libro NO está disponible si tiene un alquiler activo (ACTIVO o ATRASADO)
        activo = Alquiler.objects.filter(
            libro=self.libro,
            fecha_devolucion_real__isnull=True,
            estado__in=["ACTIVO", "ATRASADO"]
        )

        # Si estoy editando este mismo alquiler, lo excluyo
        if self.pk:
            activo = activo.exclude(pk=self.pk)

        if activo.exists():
            raise ValidationError("Este libro ya está alquilado y no está disponible.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


