-**DAMY - Cotizador de Traslados**

Aplicación web desarrollada para resolver el siguiente problema: Cuando una persona requiere un servicio de transporte por una app (Uber,Didi, Cabify) usualmente ingresa a su aplicacion favorita o mas usada, realiza la solicitud y, si el tiempo de espera y/o el precio no le acomodan, abre otra app y realiza lo mismmo. En ocasiones las personas abren las tres apps mas populars y solicitan su viaje en las tres a ver cual llega primero. Esta App busca optimizar ese proceso al comparar en un solo lugar los precios y tiempos de espera entre distintas aplicaciones de transporte, con el ingreso por parte del usuario del origen y destino, y elegir de acuerdo a lo que mejor le convenga, en cual aplicacion hacer su viaje.
Los datos de las rutas y de las tarifas y tiempos de las aplicaciones fueron simuladas en el admin.py de Django.

-**Tecnologías utilizadas**
* Backend: Django 4.x, Python 3.x
* Frontend: HTML5, CSS3, Bootstrap 5
* Base de datos: SQLite (por defecto) o MySQL/PostgreSQL

-**Instalación y configuración**
* Clonar el repositorio
* Crear entorno virtual e instalar dependencias
* Configurar base de datos en settings.py
* Configurar archivos estáticos y media
* Aplicar migraciones y crear superusuario
* Ejecutar servidor

-**Uso**
* Inicia sesión con tu usuario.
* Ingresa origen y destino en el formulario.
* Haz clic en COTIZAR → se abrirá un modal con las cotizaciones.
* Selecciona una app y redirígete a su sitio oficial.
* Consulta tus solicitudes en “Mis Cotizaciones”:
* Editar: recalcula precio/tiempo si cambias origen, destino o app.
* Eliminar: borra la solicitud del listado.

-**Autor:**
Proyecto desarrollado por Karen Herrera como parte de su formación en Full Stack Python/Django.

