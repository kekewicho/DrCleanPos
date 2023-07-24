# DrCleanPOS

Punto de venta para lavandería (Desktop app), desarrollado en Kivy-Python. El proyecto fue desarrollado para Lavandería Dr. Clean (empresa ya existente en México), por lo que en caso de replicar, deberás cambiar logos y nombre en el MainScreen.

El sistema esta pensado para incorporar un sistema de plataformas destinadas a los diferentes stakeholders alrededor de una lavandería: Cliente, Repartidor y Cajero.

## Quick Start

La app incorpora Firebase Realtime Database para el almacenamiento de la información, por lo que deberás obtener tu API KEY e incorporarla en el archivo database.py. Adicional a ello deberás contemplar la siguiente estructura en tu base de datos:

### Para almacenar los clientes:
> DBPATH/clientes/

### Para almacenar la informacion de cada nota de servicios
> DBPATH/notas/

### Para almacenar los servicios con sus precios
> DBPATH/servicios/

Tambien se consumme la API de Google Maps Platform, por lo que deberás obtener la API KEY desde el sitio de Google Maps Platform y colocarlo en el archivo ClientesScreen.py

Ambas API KEY deberas colocarlas en los archivos indicados, o bien, no modificar el archivo y colocarlas en tu archivo .env con los indices correctos.
