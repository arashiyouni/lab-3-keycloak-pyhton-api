# # Valores de entrada y estructura de la respuesta
from pydantic import BaseModel

class EstudianteBase(BaseModel):
    carnet: str
    name: str
    lastname: str
    university_carrer: str

class EstudianteCreate(EstudianteBase):
    pass

class getEstudiante(EstudianteBase):
    carnet: str

    class Config:
        from_attributes = True
