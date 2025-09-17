from rest_framework import serializers
from biblioteca.models import Autor, Categoria, Libro, Prestamo
from datetime import date

class AutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    libros_publicados = serializers.SerializerMethodField()
    class Meta:
        model = Autor
        fields = ["nombre", "apellido", "fecha_nacimiento", "nacionalidad", "biografia", "activo", "nombre_completo", "libros_publicados"]
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    def get_libros_publicados(self, obj):
        return obj.libros.count() #aqui usamos el related_name definido en el modelo Libro y por eso es libros
    
    # Validacion personalizada 
    def validate_fecha_nacimiento(self, value):
        if value >= date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser en el futuro")
        return value
    


class CategoriaSerializer(serializers.ModelSerializer):
    total_libros = serializers.SerializerMethodField()
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "total_libros"]
    def get_total_libros(self, obj):
        return obj.libro_set.count()   #aqui usamos el related_name por defecto que es el nombre del modelo en minusculas seguido de _set
    
class LibroSerializer(serializers.ModelSerializer):
    estado_legible = serializers.SerializerMethodField()
    
    autorFK = AutorSerializer(read_only=True)
    categoriaFK = CategoriaSerializer(read_only=True)
    class Meta:
        model = Libro
        fields = ["titulo", "isbn", "fecha_publicacion", "numero_paginas", "descripcion", "autor", "autorFK", "categoria", "categoriaFK" ,"estado", "precio", "fecha_agregado", "estado_legible"]
    def get_estado_legible(self, obj):
        return obj.get_estado_display()  #metodo que genera django para campos con choices solo basta con poner get_<nombre_campo>_display() y django lo reconoce
    
    # Validacion personalizada
    def validate_isbn(self, value):
        if len(value) != 13 or not value.isdigit():
            raise serializers.ValidationError("El ISBN debe tener 13 numeros")
        return value
    def validate_numero_paginas(self, value):
        if value <= 0:
            raise serializers.ValidationError("El numero de paginas no puede ser menor o igual a 0 ")
        return value
    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo")
        return value
    

class PrestamoSerializer(serializers.ModelSerializer):
    dias_restantes = serializers.SerializerMethodField()
    esta_vencido = serializers.SerializerMethodField()
    
    libroFK = LibroSerializer(read_only=True)
    class Meta:
        model = Prestamo
        fields = ["usuario", "libro", "libroFK","fecha_prestamo", "fecha_devolucion_esperada", "fecha_devolucion_real", "activo", "dias_restantes", "esta_vencido"]
    def get_dias_restantes(self, obj):
        dias = (obj.fecha_devolucion_esperada - date.today()).days #calcula la diferencia en dias entre dos fechas
        if dias < 0:
            return "Vencido"
        elif dias == 0:
            return "Hoy es el último día"
        else:
            return f"Quedan {dias} dias"
    def get_esta_vencido(self, obj):
        return date.today() > obj.fecha_devolucion_esperada and obj.fecha_devolucion_real is None #si aun no se registra feccha de devolucion real
                                                                                                  #y la fecha actual es mayor a la esperada entonces esta vencido

    # Validacion personalizada
    def validate(self, data):
        if data["fecha_devolucion_esperada"] < data["fecha_prestamo"]:
            raise serializers.ValidationError("La fecha de devolucion esperada no puede ser anterior a la fecha de prestamo")
        return data
    def validate_fecha_devolucion_esperada(self, value):
        if value < date.today():
            raise serializers.ValidationError("La fecha de devolucion esperada no puede ser en el pasado")
        return value
    
    

