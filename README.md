#  Big Tools: Sistema Experto de Diagnóstico y Mantenimiento

## Descripción del Proyecto

Este proyecto implementa un **Sistema Experto Multimáquina** en Python, diseñado para asistir a técnicos y personal de Big Tools en el diagnóstico de fallas y la guía de mantenimiento paso a paso para equipos industriales (Generadores, Hidrolavadoras, etc.).

La lógica de diagnóstico utiliza un **Motor de Inferencia** (lógica Akinator / Encadenamiento de Reglas) que consume una **Base de Conocimiento (BK)** modular en formato JSON, derivada directamente de los manuales técnicos (Generac, Cummins, Kärcher, Lincoln).

### Características Clave:

* **Diagnóstico Conversacional:** Interfaz de Chatbot para guiar al usuario a través de preguntas de Sí/No.
* **Base de Conocimiento Modular:** Fácilmente actualizable por administradores a través de un endpoint seguro.
* **Backend Seguro:** Implementación de una API REST con **Flask** que utiliza autenticación `Basic` basada en roles (`administrador` vs. `tecnico_libre`).
* **Persistencia de Estado:** El motor de inferencia gestiona el estado de la sesión, permitiendo un flujo lógico de diagnóstico y solución procedural.

***

## Estructura del Repositorio

| Carpeta / Archivo | Contenido | Rol |
| :--- | :--- | :--- |
| `backend/api/app.py` | Servidor Flask, Lógica de autenticación, Endpoints API. | **Servidor API** |
| `backend/core/` | Clases principales: `BaseConocimientos` y `MotorDiagnostico`. | **Motor de Inferencia** |
| `backend/base_conocimiento.json` | Reglas de diagnóstico (Fallas, Síntomas, Pasos de Solución) extraídas de los manuales. | **Base de Conocimiento** |
| `frontend/index.html` | Interfaz del Chatbot (HTML/JavaScript) y lógica de comunicación. | **Interfaz de Usuario (Chatbot)** |
| `backend/requirements.txt` | Dependencias Python (Flask, werkzeug). | Configuración |

***

##  Instalación y Ejecución

Sigue estos pasos para poner el sistema en funcionamiento en tu entorno local.

### Requisitos Previos

* Python 3.8+
* Git
* Un navegador web para el `frontend`.

### 1. Clonar el Repositorio e Instalar Dependencias

```bash
# 1. Clonar el repositorio
git clone <URL_DE_TU_REPOSITORIO>
cd BigTools_Expert_System/

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate   # Windows

# 3. Instalar dependencias del backend
pip install -r backend/requirements.txt
