import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:ShaAric%402024@localhost:5432/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
