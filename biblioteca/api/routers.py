from django.urls import path, include
from biblioteca.api.views import AutorListCreateView, AutorDetailView, CategoriaListCreateView, CategoriaDetailView, LibrosListCreateViev, LibrosDetailView, RegisterView, LogoutView, PerfilView, CambioPasswordView, PrestamosListCreateView, DevolverPrestamosView, EstadisticasUsuarioSelfView, EstadisticasGlobalAdminView, EstadisticasUsuariosAdminView, EditarPrestamoView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("api/autores/", AutorListCreateView.as_view(), name="autor-list-create"),
    path("api/autores/<int:id>/", AutorDetailView.as_view(), name="autor-detail"),
    path("api/categorias/", CategoriaListCreateView.as_view(), name="categoria-list-create"),
    path("api/categorias/<int:id>/", CategoriaDetailView.as_view(), name="categoria-detail"),
    path("api/libros/", LibrosListCreateViev.as_view(), name="libro-list-create"),
    path("api/libros/<int:id>/", LibrosDetailView.as_view(), name="libro-detail"),
    #registro
    path("api/auth/registro/", RegisterView.as_view(), name="register"),
    #login
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #cierre de sesion
    path("api/auth/logout", LogoutView.as_view(), name="logout"),
    #perfil usuario
    path("api/auth/perfil", PerfilView.as_view(), name= "perfil"),
    #cambio contraseña
    path("api/auth/cambiar-password/", CambioPasswordView.as_view(), name="cambio-password"),
    #prestamos
    path("api/prestramo/", PrestamosListCreateView.as_view(), name="prestamo-list-create"),
    path("api/prestamo/devolver/<int:id>/", DevolverPrestamosView.as_view(), name="prestamo-devolver"),
    path("api/prestamo/<int:id>/", EditarPrestamoView.as_view(), name="prestamo-editar"),
    #estadisticas prestamos
    path("api/prestamo/estadistica/usuario/", EstadisticasUsuarioSelfView.as_view(), name="prestamo-estadistica-usuario"),
    path("api/prestamo/estadistica/admin/<int:id>/", EstadisticasUsuariosAdminView.as_view(), name="prestamo-estadistica-admin-id"),
    path("api/prestamo/estadistica/admin/", EstadisticasGlobalAdminView.as_view(), name="prestamo-estadistica-admin")

    

]