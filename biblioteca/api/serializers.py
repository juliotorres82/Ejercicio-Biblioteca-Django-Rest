from rest_framework import serializers
from biblioteca.models import Autor, Categoria, Libro, Prestamo
from datetime import date, timedelta # para manejar tiempo y dias
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class AutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    libros_publicados = serializers.SerializerMethodField()
    class Meta:
        model = Autor
        fields = ["id","nombre", "apellido", "fecha_nacimiento", "nacionalidad", "biografia", "activo", "nombre_completo", "libros_publicados"]
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
        fields = ["id", "nombre", "descripcion", "total_libros"]
    def get_total_libros(self, obj):
        return obj.libro_set.count()   #aqui usamos el related_name por defecto que es el nombre del modelo en minusculas seguido de _set
    
class LibroSerializer(serializers.ModelSerializer):
    estado_legible = serializers.SerializerMethodField()
    
    autorFK = AutorSerializer(source="autor", read_only=True)
    categoriaFK = CategoriaSerializer(source="categoria" , read_only=True)
    class Meta:
        model = Libro
        fields = ["id","titulo", "isbn", "fecha_publicacion", "numero_paginas", "descripcion", "autor", "autorFK", "categoria", "categoriaFK" ,"estado", "precio", "fecha_agregado", "estado_legible"]
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
    def validate_autor(self, value):
        if not value.activo:
            raise serializers.ValidationError("El autor debe de estar activo")
        return value
    
    
class PrestamoSerializer(serializers.ModelSerializer):
    dias_restantes = serializers.SerializerMethodField()
    esta_vencido = serializers.SerializerMethodField()
    
    libroFK = LibroSerializer(source="libro" ,read_only=True)
    class Meta:
        model = Prestamo
        fields = ["usuario", "libro", "libroFK","fecha_prestamo", "fecha_devolucion_esperada", "fecha_devolucion_real", "activo", "dias_restantes", "esta_vencido"]
        read_only_fields = ["usuario","fecha_devolucion_esperada", "fecha_devolucion_real", "activo"] #ya no puede ser escrita por el usuario
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
    """
    def validate_fecha_devolucion_esperada(self, value):
        if value < date.today():
            raise serializers.ValidationError("La fecha de devolucion esperada no puede ser en el pasado")
        return value
   """ 
    def validate(self, data):
        #fecha devolucion no puede ser menor a fecha prestamo
        """
        if data["fecha_devolucion_esperada"] < data["fecha_prestamo"]:
            raise serializers.ValidationError("La fecha de devolucion esperada no puede ser anterior a la fecha de prestamo")
        """
        # para que solo admin pueda seleccionar id de usuario en el prestamo
        request = self.context.get("request")
        usuario = self.initial_data.get("usuario")

        if not request.user.is_staff:
            data["usuario"]=request.user
        else:
            if usuario:
                try:
                    data["usuario"] = User.objects.get(id=usuario)
                except User.DoesNotExist:
                    raise serializers.ValidationError("El usuario especificado no existe")
            else:
                data["usuario"] = request.user

                    



        #max 3 libros por usuario
        user = self.context["request"].user  # el usuario autenticado
        prestamos_activos = Prestamo.objects.filter(usuario=user, activo=True).count() #cuenta cuantas veces aparece un usuario con activo en True
    
        if prestamos_activos >= 3:
            raise serializers.ValidationError("Máximo 3 préstamos activos por usuario")
        
        #solo libros disponibles
        libro = data["libro"]
        if libro.estado != "disponible":
            raise serializers.ValidationError("Solo libros disponibles pueden prestarse")
        
        #no prestar si hay libro vencido

        usuario = data["usuario"]
        vencido = Prestamo.objects.filter(
            usuario = usuario,
            activo = True,
            fecha_devolucion_esperada__lt = date.today(), #si es menor a la fecha de hoy
            fecha_devolucion_real__isnull = True 

        ).exists()

        if vencido: 
            raise serializers.ValidationError("No se pueden prestar mas libros porque ya se vencio la fecha de devolucion del anterior libro")

        
        return data
    

    def create(self, validated_data):
        
        #cambia el estado del libro de disponible a prestado
        libro = validated_data["libro"]
        libro.estado = "prestado"
        libro.save()

        #fecha de devolucion esperada ahora sera automaticamente a los 15 dias del registro
        validated_data["fecha_devolucion_esperada"] = date.today()+ timedelta(days=15)
        
        
        return super().create(validated_data)


#todos los validate o create deben de estar juntos porque solo se toma el ultimo metodo y los demas se sobreescriben
"""
    #cambia el estado de un libro de disponible a prestado
    def create(self, validated_data):
        libro = validated_data["libro"]
        libro.estado = "prestado"
        libro.save()
        return super().create(validated_data)

    #15 dias de prestamo
    def create(self, validated_data):
        validated_data["fecha_devolucion_esperada"] = date.today()+ timedelta(days=15)
        return super().create(validated_data)
""" 


"""
    def validate(self, data):
        if data["fecha_devolucion_esperada"] < data["fecha_prestamo"]:
            raise serializers.ValidationError("La fecha de devolucion esperada no puede ser anterior a la fecha de prestamo")
        return data
    
    #max 3 libros por usuario
    def validate(self, data):
        user = self.context["request"].user  # el usuario autenticado
        prestamos_activos = Prestamo.objects.filter(usuario=user, activo=True).count() #cuenta cuantas veces aparece un usuario con activo en True
    
        if prestamos_activos >= 3:
            raise serializers.ValidationError("Máximo 3 préstamos activos por usuario")
        return data
    
    #solo libros disponibles
    def validate(self, data):
        libro = data["libro"]
        if libro.estado != "disponible":
            raise serializers.ValidationError("Solo libros disponibles pueden prestarse")
        return data
    
        # no prestar si hay libro vencido
    def validate(self, data):
        usuario = data["usuario"]
        vencido = Prestamo.objects.filter(
            usuario = usuario,
            activo = True,
            fecha_devolucion_esperada__lt = date.today(), #si es menor a la fecha de hoy
            fecha_devolucion_real__isnull = True 

        ).exists()

        if vencido: 
            raise serializers.ValidationError("No se pueden prestar mas libros porque ya se vencio la fecha de devolucion del anterior libro")

        return data
        """     
# serializer para editar un reigistro
class EditarPrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestamo
        # Campos que se pueden actualizar manualmente
        fields = ["usuario", "libro"]

#serializer simbolico para devolver libro
class DevolverPrestamoSerializer(serializers.Serializer):
    regresar = serializers.BooleanField(required=True, help_text="Debe ser True para confirmar la devolucion")

        

# Registro

class RegistroSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True, required=True, validators=[validate_password]) #cuando termines quitas el comentario, para que funcione el de validacion de contraseña
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]

    #comparar contraseñas para saber si usuario la escribio correctamente
    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return data

    #encriptacion
    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Usario perfil
class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id","username"] #estos campos no pueden ser editados

# Cambiar contraseña
class CambiarPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True,  write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        #validate_password(attrs["new_password"])
        
        return attrs
    

