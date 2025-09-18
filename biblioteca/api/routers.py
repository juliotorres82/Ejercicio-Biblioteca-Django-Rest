from django.urls import path, include
from biblioteca.api.views import AutorListCreateView, AutorDetailView, CategoriaListCreateView, CategoriaDetailView, LibrosListCreateViev, LibrosDetailView

urlpatterns = [
    path("api/autores/", AutorListCreateView.as_view(), name="autor-list-create"),
    path("api/autores/<int:id>/", AutorDetailView.as_view(), name="autor-detail"),
    path("api/categorias/", CategoriaListCreateView.as_view(), name="categoria-list-create"),
    path("api/categorias/<int:id>/", CategoriaDetailView.as_view(), name="categoria-detail"),
    path("api/libros/", LibrosListCreateViev.as_view(), name="libro-list-create"),
    path("api/libros/<int:id>/", LibrosDetailView.as_view(), name="libro-detail")
    
    

]