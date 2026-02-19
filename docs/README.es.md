# MTGA

<picture>
    <img alt="MTGA" src="https://github.com/BiFangKNT/mtga/blob/gui/icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](../README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](README.fr.md) [![Documentação em Português (Brasil)](https://img.shields.io/badge/docs-Português-purple)](README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](README.ru.md)

## Introducción

MTGA es una solución de proveedor de servicios de modelos fijos para IDE basada en proxy local, compatible con Windows y macOS.

**Nota: Este proyecto actualmente solo admite APIs en formato openai, por favor confirma. Otros formatos pueden convertirse al formato openai antes de su uso.**

<details>
  <summary>No puedes ver nada~~</summary>
  <br>
  <p>¡MTGA significa Make T Great Again!</p>
 </details>

## Índice

- [MTGA](#mtga)
  - [Introducción](#introducción)
  - [Índice](#índice)
  - [Registro de cambios](#registro-de-cambios)
    - [v1.2.0 (Última versión)](#v120-última-versión)
    - [v1.1.1](#v111)
    - [v1.1.0](#v110)
    - [v1.0.0](#v100)
  - [Inicio rápido](#inicio-rápido)
    - [Usuarios de Windows (método de inicio con un clic en GUI)](#usuarios-de-windows-método-de-inicio-con-un-clic-en-gui)
    - [Para usuarios de macOS (instalación de aplicación)](#para-usuarios-de-macos-instalación-de-aplicación)
      - [Método de instalación](#método-de-instalación)
      - [Modo de uso](#modo-de-uso)
  - [macOS Resolución del problema de "Paquete dañado"](#macos-resolución-del-problema-de-paquete-dañado)
    - [Solución gráfica](#solución-gráfica)
    - [Solución por línea de comandos (cli)](#solución-por-línea-de-comandos-cli)
  - [Iniciar desde script](#iniciar-desde-script)
    - [Paso 0: Preparación del entorno](#paso-0-preparación-del-entorno)
      - [Windows](#windows)
        - [Paso 1: Generar un certificado autofirmado](#paso-1-generar-un-certificado-autofirmado)
        - [Paso 2: Hacer que Windows confíe en tu certificado de CA](#paso-2-hacer-que-windows-confíe-en-tu-certificado-de-ca)
        - [Paso 3: Modificar el archivo Hosts](#paso-3-modificar-el-archivo-hosts)
        - [Paso 4: Ejecutar el servidor proxy local (Python)](#paso-4-ejecutar-el-servidor-proxy-local-python)
        - [Paso 5: Configurar Trae IDE](#paso-5-configurar-trae-ide)
      - [macOS](#macos)
  - [😎 Mantenerse actualizado](#-mantenerse-actualizado)
  - [Referencias](#referencias)

---

## Registro de cambios

### v1.2.0 (Última versión)

- 🔄 **Reestructuración de la arquitectura de mapeo de modelos** - Cambio de "mapeo uno a uno" a arquitectura de "modelo de mapeo unificado"
  - El extremo trae usa un ID de modelo de mapeo unificado, MTGA alterna el modelo backend real a través del grupo de configuración
  - El servidor proxy soporta el mapeo de ID de modelo y la verificación de autenticación MTGA
  - La configuración global soporta el ajuste del ID de modelo de mapeo y la clave de autenticación MTGA
- ⚡ **Optimización de la gestión de grupos de configuración** - Reestructuración de campos de grupo de configuración y lógica de validación
  - El nombre del grupo de configuración es opcional, URL de API, ID del modelo real y clave API son obligatorios
  - Se elimina el campo de ID del modelo objetivo, cambiado a configuración de mapeo global
  - Cambio de nombre en encabezados de tabla de grupo de configuración, compatible hacia atrás con archivos de configuración antiguos
- 🧪 **Nueva función de pruebas automatizadas** - Sistema completo de prueba de conexión de modelos
  - Prueba automática de conexión del modelo tras guardar configuración (GET `/v1/models/{modelo_id}`)
  - Función de prueba manual disponible, soporta prueba de complemento de chat (POST `/v1/chat/completions`)
  - Salida detallada de registros de pruebas, incluyendo contenido de respuesta y estadísticas de consumo de tokens
- 🎯 **Mejora de la experiencia del usuario** - Nuevo botón de prueba activa y consejos detallados
  - Botón de prueba activa soporta tooltip con aviso del riesgo de consumo de tokens
  - Prueba asíncrona para evitar bloqueo de interfaz, mecanismo completo de manejo de errores
  - Visualización segura de clave API (enmascaramiento)

<details>
<summary>Versiones anteriores</summary>

### v1.1.1

- 🐛 **Corregido problema con la función de modificación de hosts** - Solucionado problema de caracteres de nueva línea anómalos al modificar el archivo hosts

### v1.1.0

- ✨ **Nueva función de gestión de datos de usuario** - Versión de archivo único admite almacenamiento persistente de datos de usuario
  - Ubicación de almacenamiento de datos: Windows `%APPDATA%\MTGA\`, macOS/Linux `~/.mtga/`
  - Admite copia de seguridad, restauración y eliminación de datos de usuario
  - Configuración, certificados SSL, copia de seguridad de hosts se guardan automáticamente de forma persistente
- 🔧 **Optimizada la construcción de archivo único** - Mejorado `build_onefile.bat`, admite variables de número de versión
- 🎯 **Mejorada la interfaz de usuario** - Añadido botón de actualización de lista de grupos de configuración, optimizado diseño de interfaz
- 📖 **Documentación mejorada** - Añadida guía de construcción de archivo único, actualizada documentación del proyecto

### v1.0.0

- ✅ **Adaptado para Mac OS** - Admite método de instalación de aplicación para macOS
- 🔄 **Proveedor de servicios predeterminado cambiado** - De DeepSeek a OpenAI
- 📦 **Refactorización de archivos** - Archivos relacionados con ds renombrados a formato `*_ds.*` para archivo
- 🌐 **Formato de URL de API cambiado** - De `https://your-api.example.com/v1` a `https://your-api.example.com`

</details>

---

## Inicio rápido

### Usuarios de Windows (método de inicio con un clic en GUI)

1. Descarga la última versión de `MTGA_GUI-v{versión}-x64.exe` desde [GitHub Releases](https://github.com/BiFangKNT/mtga/releases)
2. Ejecuta el archivo exe descargado haciendo doble clic (se requieren permisos de administrador)
3. En la interfaz gráfica abierta, completa la URL de la API y el ID del modelo
   - **La URL de la API solo necesita el dominio (el número de puerto es opcional, si no lo entiendes no lo completes), no es necesario incluir la ruta posterior, por ejemplo: `https://your-api.example.com`**
   - **Si deseas habilitar capacidades multimodales, puedes mapear el nombre del modelo al nombre del modelo multimodal incorporado:**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
4. Haz clic en el botón "Iniciar todos los servicios con un clic"
5. Espera a que el programa complete automáticamente las siguientes operaciones:
   - Generar e instalar el certificado
   - Modificar el archivo hosts
   - Iniciar el servidor proxy
6. Una vez completado, configura el IDE según [Paso 5: Configurar Trae IDE](#第-5-步配置-trae-ide)

> [!NOTE]
>
> - La primera ejecución puede requerir permitir el acceso del firewall
> - La versión de un solo archivo admite el almacenamiento persistente de datos de usuario, la configuración y los certificados se guardan automáticamente

### Para usuarios de macOS (instalación de aplicación)

#### Método de instalación

1. Descarga la última versión de `MTGA_GUI-v{versión}-aarch64.dmg` desde [GitHub Releases](https://github.com/BiFangKNT/mtga/releases)
2. Haz doble clic en el archivo DMG, el sistema montará automáticamente el paquete de instalación
3. Arrastra `MTGA_GUI.app` a la carpeta `Applications`
4. Inicia la aplicación desde Launchpad o la carpeta Applications

#### Modo de uso

1. Inicia `MTGA_GUI.app` (la primera ejecución puede requerir permitir la ejecución en Preferencias del Sistema)
2. En la interfaz gráfica, completa:
   - **URL de la API**: tu dirección de servicio API (por ejemplo: `https://your-api.example.com`)
   - **Si deseas habilitar capacidades multimodales, puedes mapear el nombre del modelo al nombre del modelo multimodal incorporado:**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
3. Haz clic en el botón "Iniciar todos los servicios con un clic"
4. El programa completará automáticamente:
   - Generar e instalar el certificado SSL en el llavero del sistema
   - Modificar el archivo `/etc/hosts` (se requieren permisos de administrador)
5. Es necesario confiar manualmente en el certificado generado en la ventana del llavero que se abre, el nombre predeterminado es `MTGA_CA`
6. Inicia el servidor proxy local
7. Completa la configuración según la [Configuración del IDE Trae](#第-5-步配置-trae-ide) a continuación

> [!NOTE]
>
> - La instalación del certificado y la modificación del archivo hosts requieren permisos de administrador.
> - Si aparece el mensaje "Paquete dañado", consulte [macOS Resolución del problema de "Paquete dañado"](#macos-resolución-del-problema-de-paquete-dañado).

## macOS Resolución del problema de "Paquete dañado"

Si al iniciar `MTGA_GUI.app` aparece este mensaje:

<img width="244" height="223" alt="app corrupted" src="../images/app-corrupted.png?raw=true" />

**Haga clic en Cancelar**. Luego siga los pasos siguientes para resolverlo:

### Solución gráfica

1. Vaya a [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest) y descargue `Sentinel.dmg`.
2. Haga doble clic en el archivo `Sentinel.dmg` y arrastre `Sentinel.app` a la carpeta `Applications`.
3. Abra `Sentinel.app` desde el Launchpad o desde la carpeta Applications.
4. Arrastre el `MTGA_GUI.app` de este proyecto a la ventana izquierda de `Sentinel.app`.
   - <img width="355.33" height="373.33" alt="sentinel add app" src="../images/sentinel-add-app.png?raw=true" />

`MTGA_GUI.app` será procesado automáticamente y se iniciará.

### Solución por línea de comandos (cli)

1. Localice la ruta completa de `MTGA_GUI.app`, por ejemplo, `/Applications/MTGA_GUI.app`.
2. Abra la aplicación Terminal.
3. Ejecute el siguiente comando para firmar `MTGA_GUI.app`:
   ```zsh
   xattr -d com.apple.quarantine <ruta completa de la aplicación>
   ```
   Esto eliminará el atributo extendido `com.apple.quarantine` de `MTGA_GUI.app`.
4. Inicie `MTGA_GUI.app`.

---

## Iniciar desde script

### Paso 0: Preparación del entorno

#### Windows

- El sistema debe ser Windows 10 o superior
- Tener permisos de administrador
- Instalar el entorno Python, se recomienda Python 3.10 o superior
- Instalar Git

##### Paso 1: Generar un certificado autofirmado

Abre Git Bash:

```bash
# Cambiar al directorio ca
cd "mtga/ca"

# 1. Generar el certificado CA (ca.crt y ca.key)
./genca.sh
```

Al ejecutar `./genca.sh`, te preguntará "Do you want to generate ca cert and key? [yes/no]". Ingresa `y` y presiona Enter. Luego, te pedirá que completes cierta información:

- `Country Name (2 letter code) []`: Ingresa `CN` (u otro código de país)
- Otros campos (como State, Locality, Organization, Common Name for CA) pueden completarse según sea necesario o dejarse en blanco; se sugiere ingresar `X`. Common Name puede ser algo como `MTGA_CA`. El correo electrónico puede dejarse en blanco.

```bash
# 2. Generar el certificado SSL para api.openai.com (api.openai.com.crt y api.openai.com.key)
# Este script utilizará los archivos api.openai.com.subj y api.openai.com.cnf en el mismo directorio
./gencrt.sh api.openai.com
```

Una vez finalizada la ejecución, en el directorio `mtga\ca` encontrarás los siguientes archivos importantes:

- `ca.crt` (tu certificado de CA personalizado)
- `ca.key` (tu clave privada de CA personalizada - **no la compartas**)
- `api.openai.com.crt` (certificado SSL para el servidor proxy local)
- `api.openai.com.key` (clave privada SSL para el servidor proxy local - **no la compartas**)

##### Paso 2: Hacer que Windows confíe en tu certificado de CA

1.  Encuentra el archivo `mtga\ca\ca.crt`.
2.  Haz doble clic en el archivo `ca.crt` para abrir el visor de certificados.
3.  Haz clic en el botón "Instalar certificado...".
4.  Selecciona "Usuario actual" o "Equipo local". Se recomienda seleccionar "Equipo local" (esto requiere permisos de administrador) para que afecte a todos los usuarios.
5.  En el siguiente cuadro de diálogo, selecciona "Colocar todos los certificados en el siguiente almacén" y luego haz clic en "Examinar...".
6.  Selecciona "Entidades de certificación raíz de confianza" y luego haz clic en "Aceptar".
7.  Haz clic en "Siguiente" y luego en "Finalizar". Si aparece una advertencia de seguridad, selecciona "Sí".

##### Paso 3: Modificar el archivo Hosts

**⚠️ Advertencia: Después de realizar este paso, no podrás acceder a la API original de OpenAI. El uso de la web no se ve afectado.**

Necesitas modificar el archivo Hosts con permisos de administrador para que `api.openai.com` apunte a tu máquina local.

1.  Ruta del archivo Hosts: `C:\Windows\System32\drivers\etc\hosts`
2.  Abre este archivo con el Bloc de notas (u otro editor de texto) como administrador.
3.  Agrega la siguiente línea al final del archivo:
    ```
    127.0.0.1 api.openai.com
    ```
4.  Guarda el archivo.

##### Paso 4: Ejecutar el servidor proxy local (Python)

**Antes de ejecutar el servidor proxy:**

1.  **Instalar dependencias**:
    ```bash
    pip install Flask requests
    ```
2.  **Configurar el script**:
    - Abre el archivo `trae_proxy.py`.
    - **Modifica `TARGET_API_BASE_URL`**: Reemplázalo con la URL base real de la API con formato OpenAI del sitio al que te quieres conectar (por ejemplo: `"https://your-api.example.com"`).
    - **Confirma las rutas de los certificados**: El script leerá por defecto `api.openai.com.crt` y `api.openai.com.key` desde `mtga\ca`. Si tus certificados no están en esta ruta, modifica los valores de `CERT_FILE` y `KEY_FILE`, o copia estos dos archivos al `CERT_DIR` especificado por el script.

**Ejecutar el servidor proxy:**

Abre el Símbolo del sistema (cmd) o PowerShell **ejecutándolo como administrador** (porque necesita escuchar en el puerto 443), y luego ejecuta:

```bash
python trae_proxy.py
```

Si todo va bien, deberías ver los registros de inicio del servidor.

##### Paso 5: Configurar Trae IDE

1.  Abre e inicia sesión en Trae IDE.
2.  En el diálogo de IA, haz clic en el icono del modelo en la esquina inferior derecha y selecciona "Añadir modelo" al final.
3.  **Proveedor**: Selecciona `OpenAI`.
4.  **Modelo**: Selecciona "Modelo personalizado".
5.  **ID del modelo**: Ingresa el valor que definiste en `CUSTOM_MODEL_ID` en el script de Python (por ejemplo: `my-custom-local-model`).
6.  **Clave de API**:
    - Si tu API de destino requiere una clave de API y Trae la pasará a través de `Authorization: Bearer <key>`, entonces la clave ingresada aquí será reenviada por el proxy de Python.
    - Al configurar OpenAI en Trae, la clave de API está relacionada con la configuración `remove_reasoning_content`. Nuestro proxy de Python no maneja esta lógica, simplemente reenvía el encabezado Authorization. Puedes intentar ingresar la clave requerida por tu API de destino, o una clave arbitraria con formato `sk-xxxx`.

7.  Haz clic en "Añadir modelo".
8.  Regresa al cuadro de chat de IA y selecciona el modelo personalizado que acabas de añadir en la esquina inferior derecha.

Ahora, cuando interactúes con este modelo personalizado a través de Trae, las solicitudes deberían pasar a través de tu proxy local de Python y ser reenviadas a la `TARGET_API_BASE_URL` que configuraste.

**Consejos para la resolución de problemas:**

- **Conflicto de puertos**: Si el puerto 443 ya está ocupado (por ejemplo, por IIS, Skype u otro servicio), el script de Python fallará al iniciarse. Debes detener el servicio que está utilizando ese puerto, o modificar el script de Python y Nginx (si se utiliza) para que escuchen en otro puerto (aunque esto es más complejo porque Trae tiene codificado de forma rígida el acceso al puerto 443 de `https://api.openai.com`).
- **Firewall**: Asegúrate de que el firewall de Windows permita conexiones entrantes en el puerto 443 para Python (aunque se trate de conexiones locales `127.0.0.1`, normalmente no requiere configuración especial del firewall, pero vale la pena verificarlo).
- **Problemas de certificado**: Si Trae reporta errores relacionados con SSL/TLS, verifica cuidadosamente que el certificado de CA esté instalado correctamente en las "Entidades de certificación raíz de confianza", y que el proxy de Python cargue correctamente los archivos `api.openai.com.crt` y `.key`.
- **Registros del proxy (logs)**: El script de Python imprimirá algunos registros que pueden ayudarte a diagnosticar problemas.

Esta solución está más integrada que el método directo que usa vproxy + nginx, ya que coloca la terminación TLS y la lógica del proxy en un único script de Python, lo que la hace más adecuada para una rápida validación de prototipos en Windows.

#### macOS

-> [Método de inicio del script para Mac OS](https://github.com/BiFangKNT/mtga/blob/gui/docs/README_macOS_cli.md)

---

## 😎 Mantenerse actualizado

Haz clic en los botones Star (Estrella) y Watch (Observar) en la parte superior derecha del repositorio para obtener las últimas actualizaciones.

![star to keep latest](https://github.com/BiFangKNT/mtga/blob/gui/images/star-to-keep-latest.gif?raw=true)

---

## Referencias

El directorio `ca` está referenciado desde el repositorio `wkgcass/vproxy`. ¡Gracias al experto!
