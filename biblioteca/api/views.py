from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from biblioteca.models import Autor, Categoria, Libro, Prestamo
from biblioteca.api.serializers import AutorSerializer, CategoriaSerializer, LibroSerializer, PrestamoSerializer
from rest_framework import permissions
from django.db.models import Q


# Crud para Autor
# Get y Post en una sola vista
class AutorListCreateView(APIView):
    permission_classes = [permissions.AllowAny] # cualquiera puede ver la lista de autores y crear nuevos autores
    def get(self, request):
        autores = Autor.objects.filter(activo=True) # filtro solo autores activos
        
        # filtros por query params
        # filtro por nacionalidad
        nacionalidad = request.query_params.get("nacionalidad")
        if nacionalidad:
            autores = autores.filter(nacionalidad__iexact=nacionalidad) # iexact para que ignore mayusculas y minusculas
       
        # filtro por nombre
        busqueda = request.query_params.get("busqueda")
        if busqueda:
            autores = autores.filter(
                Q(nombre__icontains=busqueda) | Q(apellido__icontains=busqueda) # icontains para que busque en cualquier parte del string y ignore mayusculas y minusculas
            ) # Q para hacer consultas complejas con OR
        
        
        serializer = AutorSerializer(autores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = AutorSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# Get, Put y Delete en una sola vista de un autor por id
class AutorDetailView(APIView):
    permission_classes = [permissions.AllowAny] # cualquiera puede ver, editar o eliminar un autor
    def get_object(self, id): # obtener un autor por id
        try:
            return Autor.objects.get(id=id)
        except Autor.DoesNotExist:
            return None
    def get(self, request, id):
        autor = self.get_object(id)
        if not autor:
            return Response({"error": "Autor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if autor.activo == False:
            return Response({"error": "Autor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AutorSerializer(autor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, id):
        autor = self.get_object(id)
        if not autor:
            return Response({"error": "Autor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AutorSerializer(autor, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, id):
        autor = self.get_object(id)
        if not autor:
            return Response({"error": "Autor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AutorSerializer(autor, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self, request, id):
        autor = self.get_object(id)
        if not autor:
            return Response({"error": "Autor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        autor.activo = False # soft delete, no lo elimina solo cambia activo a false y ya no se muestra pero sigue en la BD
        autor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    
    # Crud para categoria 
    # Get y Post en una sola vista
class CategoriaListCreateView(APIView):
    permission_classes = [permissions.AllowAny] # esto solo es para pruebas, en produccion solo admin puede crear categorias
    def get(self, request):
        categoria = Categoria.objects.all()
        serializer = CategoriaSerializer(categoria, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# Get, Put y Delete en una sola vista de una categoria por id
class CategoriaDetailView(APIView):
    permission_classes = [permissions.AllowAny] 
    def get_object(self, id):  # obtener una categoria por id
        try:
            return Categoria.objects.get(id=id)
        except Categoria.DoesNotExist:
            return None
    def get(self, request, id):
        categoria = self.get_object(id) # aqui usamos el metodo get_object para obtener la categoria
        if not categoria:
            return Response({"error": "Categoria no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategoriaSerializer(categoria) # aqui usamos el serializer para serializar la categoria
        return Response(serializer.data, status=status.HTTP_200_OK) # devolvemos la categoria serializada
    def put(self, request, id):
        categoria = self.get_object(id)
        if not categoria:
            return Response({"error": "Categoria no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategoriaSerializer(categoria, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, id):
        categoria = self.get_object(id)
        if not categoria:
            return Response({"error": "Categoria no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategoriaSerializer(categoria, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self, request, id):
        categoria = self.get_object(id)
        if not categoria:
            return Response({"error": "Categoria no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        categoria.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #Crud para libro
    #Get y post en una sola vista
class LibrosListCreateViev(APIView):
    permission_classes = [permissions.AllowAny] # esto solo es para pruebas se cambiara en produccion a que solo admin pueda crear libros
    def get(self, request):
        #libro = Libro.objects.all()
        libro = Libro.objects.select_related("autor", "categoria").order_by("id").all() # optimizar consultas con select_related para relaciones ForeignKey
        # filtros por query params
        # filtro por autor
        autor = request.query_params.get("autor")
        if autor:
            q = Q(autor__nombre__iexact=autor) | Q(autor__apellido__iexact=autor)
            if autor.isdigit():          # solo si el valor es numérico
                q |= Q(autor__id=int(autor))
            libro = libro.filter(q)

        #filtro por categoria
        categoria = request.query_params.get("categoria")
        if categoria:
            q = Q(categoria__nombre__iexact=categoria)
            if categoria.isdigit():
                q |= Q(categoria__id=int(categoria))
            libro = libro.filter(q)
        
        #filtro por estado
        estado = request.query_params.get("estado")
        if estado:
            libro = libro.filter(estado__iexact=estado)
        
        #filtro por precio
        precio_min = request.query_params.get("precio_min")
        precio_max = request.query_params.get("precio_max")
        if precio_min:
            try:
                precio_min= float(precio_min)
                libro = libro.filter(precio__gte=precio_min)
            except ValueError:
                pass

        if precio_max:
            try:
                precio_max=float(precio_max)
                libro = libro.filter(precio__lte=precio_max)
            except ValueError:
                pass
        #filtro por año
        anio = request.query_params.get("anio")
        if anio:
            libro = libro.filter(fecha_publicacion__year=anio)
            
        #filtro por busqueda
        busqueda = request.query_params.get("busqueda")
        if busqueda:
            libro = libro.filter(
                Q(autor__nombre__icontains=busqueda)|
                Q(autor__apellido__icontains=busqueda)|
                Q(categoria__nombre__icontains=busqueda)|
                Q(estado__icontains=busqueda)|
                Q(descripcion__icontains=busqueda)
            )
        #ordenamiento por multiples campos
        ordering = request.query_params.get("ordering")
        if ordering:
            #soportar multiples campos al meterlos en una lista separados por coma
            campos = [campo.strip() for campo in ordering.split(",") if campo.strip()]
            if campos:
                libro = libro.order_by(*campos)


        serializer = LibroSerializer(libro, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = LibroSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    #Get, put,patch,delete en una sola vista de un solo libro por ID
class LibrosDetailView(APIView):
    permission_classes = [permissions.AllowAny] # esto solo es para preba se cambiara en produccion a que solo admin pueda modificar libros
    def get_object(self, id): #obtener un libro por id
        try:
            return Libro.objects.get(id=id)
        except Libro.DoesNotExist:
            return None
    def get(self, request, id):
        libro = self.get_object(id)
        if not libro:
            return Response({"error": "Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LibroSerializer(libro)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, id):
        libro = self.get_object(id)
        if not libro:
            return Response({"error": "Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LibroSerializer(libro, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, id):
        libro = self.get_object(id)
        if not libro:
            return Response({"error": "Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LibroSerializer(libro, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self, request, id):
        libro = self.get_object(id)
        if not libro:
            return Response({"error":"Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        libro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   




    

