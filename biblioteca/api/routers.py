from django.urls import path, include
from biblioteca.api.views import AutorListCreateView, AutorDetailView

urlpatterns = [
    path("api/autores/", AutorListCreateView.as_view(), name="autor-list-create"),
    path("api/autores/<int:id>/", AutorDetailView.as_view(), name="autor-detail"),
    

]