Biblioteca Personal - Proyecto Django 

Descripción
Aplicación web desarrollada con Django para la gestión de una biblioteca personal.
Permite gestionar libros, autores y editoriales, incorporando el uso de slugs
para URLs amigables y administración mediante el panel de Django.

Requisitos
- Python 3.9
- Django 4.2.1

Instalación y ejecución

1. Abrir una terminal en la carpeta del proyecto.
2. Crear y activar el entorno virtual.
3. Instalar Django:
   pip install django==4.2.1
4. Aplicar migraciones:
   python manage.py migrate
5. Ejecutar el servidor:
   python manage.py runserver
6. Abrir el navegador y acceder a:
   http://127.0.0.1:8000/

Panel de administración
Acceso al panel de administración:
http://127.0.0.1:8000/admin/

Base de datos
El proyecto incluye una base de datos SQLite (db.sqlite3) con registros de prueba:
- Libros
- Autores
- Editoriales

Funcionalidades
- Gestión de autores, editoriales y libros
- Generación automática de slugs
- Panel de administración de Django
- Listado de libros

Autor
Lorena


