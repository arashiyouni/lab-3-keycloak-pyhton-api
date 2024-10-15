from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from keycloak.keycloak_admin import KeycloakAdmin  # Cambio de importación
from keycloak.keycloak_openid import KeycloakOpenID  # Cambio de importación
from pydantic import BaseModel
import requests

from Estudiante import EstudianteDB
from database import get_db
from schemas import EstudianteCreate, getEstudiante

app = FastAPI()

# Configuración de Keycloak
KEYCLOAK_SERVER_URL = "https://makiboland.xyz/"
REALM_NAME = "laboratorio3"
CLIENT_ID = "lab3-backend"
CLIENT_SECRET = "J1FXZrjqmGEfaG1ujCRJe86JkxnfCWmb"

keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_SERVER_URL,
    username='admin',
    password='admin',
    realm_name="master",
    client_id='admin-cli',
    verify=True
)

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=CLIENT_ID,
    realm_name=REALM_NAME,
    client_secret_key=CLIENT_SECRET
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_SERVER_URL}realms/{REALM_NAME}/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_SERVER_URL}realms/{REALM_NAME}/protocol/openid-connect/token"
)

# Función para obtener la clave pública de Keycloak para verificar los tokens
def get_keycloak_public_key():
    openid_config_url = f"{KEYCLOAK_SERVER_URL}realms/{REALM_NAME}/.well-known/openid-configuration"
    response = requests.get(openid_config_url)

    if response.status_code == 200:
        jwks_uri = response.json()["jwks_uri"]
        jwks_response = requests.get(jwks_uri)

        if jwks_response.status_code == 200:
            jwks = jwks_response.json()
            public_key = jwks['keys'][0]['x5c'][0]
            return f"-----BEGIN CERTIFICATE-----\n{public_key}\n-----END CERTIFICATE-----"
    
    raise Exception("Failed to retrieve public key from Keycloak")

# Función para verificar el token JWT usando la clave pública
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        token_info = keycloak_openid.decode_token(token)
        return token_info
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Endpoint protegido
@app.get("/protected-endpoint")
async def protected_route(user_info: dict = Depends(verify_token)):
    return {"message": "Estás autenticado", "user_info": user_info}


# Crear un estudiante
@app.post("/students/", response_model=getEstudiante)
def create_student(student: EstudianteCreate, db: requests.Session = Depends(get_db)):
    try:
        db_student = EstudianteDB(**student.dict())  # Convertimos los datos de Pydantic a un dict
        db.add(db_student)
        db.commit()
        db.refresh(db_student)  # Refrescamos el objeto para obtener el carnet generado
        return db_student
    except Exception as e:
        db.rollback()  # Revertir los cambios en caso de error
        raise HTTPException(status_code=500, detail=f"Error al crear el estudiante: {str(e)}")


# Leer todos los estudiantes con manejo de excepciones
@app.get("/students/", response_model=List[getEstudiante])
def read_students(skip: int = 0, limit: int = 5, db: requests.Session = Depends(get_db), token_info: dict = Depends(verify_token)):
    try:
        username = token_info.get("username", "unknown_user")
        students = db.query(EstudianteDB).offset(skip).limit(limit).all()
        return {username, students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer los estudiantes: {str(e)}")


# Leer un estudiante por carnet con manejo de excepciones
@app.get("/students/{carnet}", response_model=getEstudiante)
def read_student(carnet: int, db: requests.Session = Depends(get_db)):
    try:
        student = db.query(EstudianteDB).filter(EstudianteDB.carnet == carnet).first()
        if student is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el estudiante: {str(e)}")


# Actualizar un estudiante con manejo de excepciones
@app.put("/students/{carnet}", response_model=getEstudiante)
def update_student(carnet: int, student_update: EstudianteCreate, db: requests.Session = Depends(get_db)):
    try:
        student = db.query(EstudianteDB).filter(EstudianteDB.carnet == carnet).first()
        if student is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        # Actualizamos los campos con los datos proporcionados
        student.name = student_update.name
        student.lastname = student_update.lastname
        student.university_carrer = student_update.university_carrer
        
        db.commit()  # Guardamos los cambios en la base de datos
        db.refresh(student)  # Refrescamos el estudiante actualizado
        return student
    except Exception as e:
        db.rollback()  # Revertir los cambios en caso de error
        raise HTTPException(status_code=500, detail=f"Error al actualizar el estudiante: {str(e)}")


# Eliminar un estudiante con manejo de excepciones
@app.delete("/students/{carnet}", response_model=getEstudiante)
def delete_student(carnet: int, db: requests.Session = Depends(get_db)):
    try:
        student = db.query(EstudianteDB).filter(EstudianteDB.carnet == carnet).first()
        if student is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        db.delete(student)
        db.commit()
        return student
    except Exception as e:
        db.rollback()  # Revertir los cambios en caso de error
        raise HTTPException(status_code=500, detail=f"Error al eliminar el estudiante: {str(e)}")