# 🌦️ Aplicación del Clima

## 📌 Descripción

Aplicación en Python que obtiene el clima actual utilizando la API de Open-Meteo.

## 🚀 Funcionalidades

* Consulta de clima por coordenadas
* Soporte para múltiples ciudades
* Caché con expiración (TTL)
* Manejo de errores robusto
* Soporte offline mediante caché

## 🧪 Pruebas

Incluye pruebas básicas para:

* Validar respuesta de la API
* Validar coordenadas inválidas
* Verificar funcionamiento del caché

## 🛠️ Tecnologías

* Python
* Requests
* ThreadPoolExecutor
* Open-Meteo API

## ▶️ Ejecución

```bash
python app.py
```

## 🔐 Consideraciones de seguridad y ética

* No se exponen claves API
* Se implementa timeout en las solicitudes
* Uso de caché para evitar sobrecarga del servicio
* Código asistido por IA, validado manualmente

## 📌 Autor

Proyecto desarrollado como práctica de consumo de APIs y buenas prácticas en desarrollo backend.

