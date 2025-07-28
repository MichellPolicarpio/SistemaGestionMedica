# �� Sistema de Gestión Médica

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0+-purple.svg)](https://getbootstrap.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4+-red.svg)](https://www.sqlalchemy.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Generation-yellow.svg)](https://www.reportlab.com/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Charts-lightgrey.svg)](https://matplotlib.org/)

**Autor:** Michell Alexis Policarpio Moran

Un sistema web completo y profesional para la gestión integral de pacientes, diagnósticos médicos, prescripciones y control de pagos en clínicas médicas. Diseñado con una interfaz moderna, funcionalidades avanzadas y reportes profesionales.

## ✨ Características Principales

### 🧑‍⚕️ **Gestión de Pacientes**
- ✅ Registro completo de información personal y médica
- ✅ Historial médico detallado (enfermedades, medicamentos, alergias)
- ✅ Cálculo automático de BMI y edad
- ✅ Búsqueda avanzada de pacientes en tiempo real
- ✅ Edición y eliminación de registros

### 📋 **Gestión Médica Profesional**
- ✅ **Diagnósticos**: Creación de diagnósticos con síntomas, tratamiento y observaciones
- ✅ **Prescripciones**: Generación automática de recetas médicas profesionales
- ✅ **PDF Profesionales**: Reportes médicos con formato clínico real
- ✅ **Cédula Profesional**: Registro dinámico del médico tratante
- ✅ **Envío por Email**: Envío automático de reportes médicos

### 💰 **Control de Pagos Integrado**
- ✅ Registro automático de pagos al crear diagnósticos
- ✅ Gestión manual de pagos por paciente
- ✅ Estadísticas financieras en tiempo real
- ✅ Historial completo de transacciones
- ✅ Múltiples métodos de pago (Efectivo, Tarjeta, Transferencia)

### 🎨 **Interfaz Moderna y Profesional**
- ✅ **Modo Oscuro/Claro**: Toggle para cambiar tema con persistencia
- ✅ **Diseño Responsivo**: Funciona perfectamente en móviles y desktop
- ✅ **Dashboard Interactivo**: Estadísticas y gráficos en tiempo real
- ✅ **Búsqueda en Tiempo Real**: AJAX para búsqueda instantánea
- ✅ **Navegación Intuitiva**: Menú profesional con todas las funciones

### 📊 **Analytics y Reportes Avanzados**
- ✅ Gráficos de distribución por edad y BMI
- ✅ Estadísticas de enfermedades y diagnósticos
- ✅ Reportes PDF profesionales con formato médico real
- ✅ Exportación de datos y envío por email
- ✅ Dashboard con métricas clave

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.9+
- MySQL Server 8.0+
- pip3

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/patient-management-system.git
cd patient-management-system
```

### 2. Instalar Dependencias
```bash
pip3 install -r requirements.txt
```

### 3. Configurar Base de Datos MySQL

#### Opción A: Script Automático (Recomendado)
```bash
python3 database_setup.py
```

#### Opción B: Configuración Manual
```sql
CREATE DATABASE patient_management;
USE patient_management;
```

### 4. Configurar Conexión a Base de Datos
Editar `app.py` línea 25:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/patient_management'
```

### 5. Ejecutar la Aplicación
```bash
python3 app.py
```

### 6. Acceder al Sistema
Abrir navegador: `http://localhost:5002`

## 🗄️ Estructura de la Base de Datos

### Tablas Principales
- **`patient`**: Información personal y médica de pacientes
- **`diagnosis`**: Diagnósticos médicos con cédula profesional
- **`prescription`**: Prescripciones médicas profesionales
- **`payment`**: Control completo de pagos y transacciones
- **`disease`**: Enfermedades del paciente
- **`medication`**: Medicamentos prescritos

### Relaciones y Funcionalidades
- ✅ Un paciente puede tener múltiples diagnósticos
- ✅ Un paciente puede tener múltiples prescripciones
- ✅ Un paciente puede tener múltiples pagos
- ✅ Diagnósticos generan prescripciones automáticamente
- ✅ Diagnósticos generan pagos automáticamente
- ✅ Eliminación en cascada de registros relacionados

## 🎯 Funcionalidades Detalladas

### 📝 Gestión de Pacientes
- **Registro Completo**: Nombre, email, teléfono, fecha de nacimiento, dirección
- **Información Física**: Altura, peso, cálculo automático de BMI
- **Historial Médico**: Enfermedades previas, medicamentos actuales, alergias, hábitos alimenticios
- **Búsqueda Avanzada**: Búsqueda por nombre, email, teléfono o dirección
- **Edición y Eliminación**: Gestión completa de registros

### 🏥 Gestión Médica
- **Diagnósticos Profesionales**: 
  - Síntomas detallados
  - Diagnóstico clínico
  - Plan de tratamiento
  - Observaciones médicas
  - Cédula profesional del médico
- **Prescripciones Automáticas**: 
  - Generación automática desde diagnósticos
  - Formato profesional de receta médica
  - Instrucciones detalladas
  - Información del médico tratante

### 💰 Control de Pagos
- **Pagos Automáticos**: Se registran automáticamente al crear diagnósticos
- **Gestión Manual**: Agregar, editar y eliminar pagos
- **Múltiples Métodos**: Efectivo, Tarjeta, Transferencia
- **Estados de Pago**: Pendiente, Completado, Cancelado
- **Estadísticas Financieras**: Ingresos totales, pagos pendientes, promedio

### 📊 Analytics y Reportes
- **Dashboard Interactivo**: Estadísticas en tiempo real
- **Gráficos Visuales**: Distribución por edad, BMI, enfermedades
- **Reportes PDF Profesionales**: 
  - Formato médico real
  - Información clínica completa
  - Firma y cédula profesional
  - Envío por email automático

### 🎨 Interfaz de Usuario
- **Modo Oscuro/Claro**: Toggle con persistencia de preferencia
- **Diseño Responsivo**: Bootstrap 5 para todas las pantallas
- **Navegación Intuitiva**: Menú profesional con todas las funciones
- **Búsqueda en Tiempo Real**: AJAX para búsqueda instantánea
- **Notificaciones**: Flash messages para feedback del usuario

## 🔧 Configuración Avanzada

### Configuración de Email
Para habilitar el envío de reportes por email:

1. Crear archivo `email_config.py`:
```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'tu-email@gmail.com',
    'sender_password': 'tu-contraseña-de-aplicación',
    'use_tls': True
}
```

2. Configurar contraseña de aplicación en Gmail

### Configuración de Base de Datos
Para cambiar la configuración de MySQL:

1. Editar `app.py` línea 25
2. Ejecutar `python3 update_database.py` si hay cambios en el esquema

## 📱 Capturas de Pantalla

### Dashboard Principal
- Estadísticas en tiempo real
- Acceso rápido a funciones principales
- Lista de pacientes recientes

### Gestión de Pacientes
- Formularios completos en español
- Búsqueda avanzada
- Información médica detallada

### Reportes PDF
- Formato profesional médico
- Información clínica completa
- Diseño institucional

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.9+**: Lenguaje principal
- **Flask 2.0+**: Framework web
- **SQLAlchemy**: ORM para base de datos
- **MySQL**: Base de datos relacional
- **ReportLab**: Generación de PDFs
- **Matplotlib/Seaborn**: Gráficos y analytics

### Frontend
- **Bootstrap 5**: Framework CSS
- **Font Awesome**: Iconos
- **JavaScript**: Interactividad
- **AJAX**: Búsqueda en tiempo real
- **CSS3**: Estilos personalizados

### Herramientas
- **pip**: Gestión de dependencias
- **Git**: Control de versiones
- **MySQL Workbench**: Gestión de base de datos

## 🚀 Despliegue

### Desarrollo Local
```bash
python3 app.py
```

### Producción
1. Configurar servidor web (Nginx/Apache)
2. Usar WSGI server (Gunicorn/uWSGI)
3. Configurar base de datos MySQL
4. Configurar variables de entorno

## 🤝 Contribuciones

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

**Autor:** Michell Alexis Policarpio Moran

- Email: michellpolicarpio@icloud.com

## 🙏 Agradecimientos

- Flask y su comunidad por el excelente framework
- Bootstrap por el diseño responsive
- MySQL por la base de datos robusta
- ReportLab por la generación de PDFs profesionales

---

**⭐ Si este proyecto te es útil, considera darle una estrella en GitHub!** 