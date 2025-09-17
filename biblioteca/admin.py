from django.contrib import admin
from biblioteca.models import Autor, Categoria, Libro, Prestamo

# Register your models here.

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'nacionalidad', 'activo']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ["titulo", "estado"]

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ["usuario", "libro", "fecha_prestamo", "fecha_devolucion_esperada", "activo"]