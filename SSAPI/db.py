import os

from dotenv import load_dotenv

load_dotenv()

DATABASEDES = DATABASESDESARROLLO = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'PALDACADB',
        'USER': 'postgres',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

DATABASEPROD = DATABASESPRODUCCION = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssapmcco_PALDACA_DB',
        'USER': 'ssapmcco_ADMIN',
        'PASSWORD': 'ADMINPALDACA12345',
        'HOST': 'localhost',
        'PORT': '',
    }
}
