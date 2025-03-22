# Aplicación deportiva con Dash de Plotly

## Descripción del Proyecto

Aplicación web de visualización de estadísticas de jugadores del Atlético de Madrid desarrollada con Dash de Plotly. La aplicación permite un análisis detallado del rendimiento de los jugadores a lo largo de la temporada.

## Características Principales

- **Autenticación de Usuarios**: Acceso mediante usuario y contraseña
- **Control de Acceso por Roles**: Diferentes vistas según el rol del usuario
- **Visualización de Estadísticas**:
  - Página 1: Estadísticas de rendimiento en partidos
  - Página 2: Datos condicionales y físicos de los jugadores

## Fuentes de Datos

- **Estadísticas de Rendimiento**: Extraídas de FBREF (CSV)
- **Datos Condicionales**: Generados dinámicamente según posición, edad y minutos jugados

## Estructura

- **assets**: 
  - Carpeta escudos
  - Carpeta imágenes
  - Carpeta jugadores
  - style.css : patrones documento 

- **callbacks**:
  - _init_.py
  - auth_callbacks.py
  - navbar_callbacks.py
  - player_stats_callbacks.py

- **components**:
  - navbar.py

- **data**:
  - csv datos competición
  - Base de datos variables condicionales inventadas
  - Archivo máster jugadores

- **ent_appmod9**: entorno a aplicar

- **layouts**:
  - login.py
  - player_stats_layout.py

- **utils**:
  - auth.py
  - data_viz.py (visualizaciones página rendimiento)
  - db_template (archivo que simula base de datos para los usuarios y contraseñas)

- **.dockerignore**

- **Dockerfile**

- **.gitignore**

- **Aplic_Atm.py**: "python Aplic_atm.py"

- **config.py**: Establece permisos

- **README.md**: Info de la Aplicación

- **requirements.txt**: pip install -r requirements.txt

## Tecnologías Utilizadas

- Python
- Dash (Plotly)
- SQLite
- Pandas
- Plotly Express
- Docker
- Git

## Instalación

1.- Clonar el repositorio: git clone https://github.com/ramon20panes/scouting_app_dash.git

2.- Crear entorno virtual: python -m venv venv

3.- Instalar dependencias: pip install -r requirements.txt

4.- Ejecutar: python Aplic_atm.py

5.- Ingresar: Dependiendo de rol, se ven algunos datos u otros

6.- Navegar por la barra de estado


## Agradecimientos

- [Alfredo Muñoz](https://github.com/Alfredomg7)

- [Federico Rabanos](https://github.com/federicorabanos)

- [Lucas Bracamonte](https://github.com/lucbra21?tab=repositories)