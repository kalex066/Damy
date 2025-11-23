-**DAMY - Cotizador de Traslados**

Aplicación web desarrollada en Django que permite comparar precios y tiempos de espera entre distintas aplicaciones de transporte (Uber, Cabify, Didi, etc.). El usuario puede ingresar un origen y destino, obtener cotizaciones en tiempo real y guardar sus solicitudes para revisarlas, editarlas o eliminarlas posteriormente.

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

