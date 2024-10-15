# # Valores de entrada y estructura de la respuesta
from pydantic import BaseModel

class EstudianteBase(BaseModel):
    name: str
    lastname: str
    university_carrer: str

class EstudianteCreate(EstudianteBase):
    pass

class getEstudiante(EstudianteBase):
    carnet: int

    class Config:
        from_attributes = True
