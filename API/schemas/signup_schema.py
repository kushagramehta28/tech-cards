from pydantic import BaseModel, EmailStr

# Standardized request body for user signup
class SignupRequest(BaseModel):
    email: EmailStr
    password: str