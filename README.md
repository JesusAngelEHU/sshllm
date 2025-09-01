# SSHLLM 🐚🤖

[![GitHub last commit](https://img.shields.io/github/last-commit/JesusAngelEHU/sshllm)](https://github.com/JesusAngelEHU/sshllm)
[![Docker Pulls](https://img.shields.io/docker/pulls/jesusangelgh/sshllm)](https://hub.docker.com/r/jesusangelgh/sshllm)

SSHLLM es un **servidor SSH simulado** que integra un **modelo de lenguaje LLM** para generar respuestas a los comandos de usuario.  
Ideal para **simulaciones, pruebas de seguridad y aprendizaje**.

---

## ✨ Características

- Shell interactivo simulado con historial de comandos y soporte ANSI.
- Respuestas generadas por LLM (por defecto `Mistral`).
- Registro completo de sesiones, comandos y desconexiones.
- Manejo de errores del LLM de forma segura (solo logs internos, usuario no ve fallos).
- Soporte multiusuario simulado y autenticación SSH realista.

---

## 🛠️ Instalación

### 1. Clonar el repositorio
git clone https://github.com/JesusAngelEHU/sshllm.git  
cd sshllm
### 2. Construir el contenedor Docker
docker build -t sshllm .
### 3. Levantar con Docker Compose
docker compose up -d
Ajusta el puerto y variables de entorno según tu entorno.

---

### 🚀 Conexion con el servidor SSH simulado:

ssh user@localhost -p 2222

Los comandos se procesan mediante un LLM y se registran en logs internos.

---

### ⚙️ Variables de entorno
LLM_SERVER_URL: URL del servidor LLM.

LLM_MODEL: Nombre del modelo de lenguaje a usar.

---

### 📄 Logs
Integrados con ELK stack, registran:

Nuevas sesiones

Autenticaciones

Comandos ejecutados

Desconexiones

Errores de conexión con LLM
