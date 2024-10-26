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


# Esquema para la creación de usuarios
class UserCreateRequest(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str

# Esquema para registrarse
class UserSignInRequest(BaseModel):
    email: str
    password: str