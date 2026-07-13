# PRD: browser-mcp

## 1. Resumen Ejecutivo

Servidor MCP (Model Context Protocol) para navegador web, diseñado para que agentes de IA puedan interactuar con un navegador de forma precisa, indetectable y con retroalimentación visual de cambios. Se diferencia de otros proyectos por ofrecer un conjunto reducido de herramientas ("toolset justo"), usar `invisible_playwright` para evitar detección, y devolver un diff HTML en cada acción para que la IA sepa exactamente qué cambió en la página.

## 2. Objetivos

- Proveer a IAs (Claude, OpenAI Agents, etc.) un control fino y comprensible del navegador.
- Minimizar la confusión del modelo con un toolset pequeño y bien definido.
- Ser indetectable como automatización mediante `invisible_playwright`.
- Dar visibilidad total del estado del navegador con diffs HTML post-acción.
- Mantener sesión persistente entre invocaciones para flujos largos.
- Soportar múltiples instancias de opencode (o cualquier cliente MCP) de forma simultánea sin conflictos, aislando cada sesión en su propio contexto de navegador.
- Poder ejecutarse en Docker (opcional) sin interferir con el sistema anfitrión.

## 3. Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Automatización | Playwright + [invisible_playwright](https://github.com/feder-cr/invisible_playwright) |
| Captcha | [2captcha-python](https://github.com/2captcha/2captcha-python) |
| Protocolo | MCP (Model Context Protocol) — librería `mcp` Python |
| Testing | pytest |
| CLI | argparse (argumentos CLI únicamente) |

## 4. Usuario Objetivo

Desarrolladores que construyen agentes autónomos con herramientas de IA, integrando browser-mcp como servidor MCP en `opencode.json` o configuraciones similares de clients MCP. No está orientado a usuarios finales directos.

## 5. Arquitectura

- **Servidor MCP** en Python que expone herramientas como recursos del protocolo MCP.
- **Navegador único, contextos múltiples**: una sola instancia de Chromium (dentro de Docker). Cada conexión MCP (sesión) recibe su propio **browser context** de Playwright (almacenamiento, cookies, sesiones aislados). Esto permite que N instancias de opencode compartan el mismo proceso de navegador sin interferencias.
- **Aislamiento por sesión**: cada sesión MCP tiene su propio contexto + su propia tab activa. Una sesión no ve ni afecta las tabs de otra sesión.
- **Snapshot pre/post**: antes de cada acción se captura el HTML del `body`, después se genera un diff contra ese snapshot.
- **Chain tool**: permite componer múltiples herramientas en una sola llamada para reducir ida y vuelta.

## 6. Ejecución

### Local (por defecto)

El servidor se ejecuta directamente en el sistema. El navegador es **visible por defecto** (`--headless` es opt-in).

### Docker (opcional)

- Imagen base con Python 3.11+ y Firefox + dependencias de Playwright.
- `docker run` expone el puerto del servidor MCP.
- `docker-compose.yml` para gestión de perfiles persistentes vía volúmenes.
- El contenedor incluye `invisible_playwright` y `2captcha-python` preinstalados.
- En Docker se recomienda usar `--headless` ya que no hay display.

### CLI args

  - `--port` (puerto del servidor MCP, opcional. Por defecto usa stdio)
  - `--headless` (flag, opt-in. Por defecto el navegador es visible)
  - `--profile` (ruta al perfil de Firefox. Si se usa Docker volume, persiste entre reinicios)
  - `--viewport-width` / `--viewport-height`
  - `--2captcha-api-key` (clave API de 2captcha, opcional. Si se provee, se habilita la tool `captcha_solve`)

## 7. Herramientas (Toolset)

Cada herramienta recibe un snapshot del HTML antes de ejecutarse y devuelve un diff de los cambios ocurridos en la página como parte de la respuesta.

### 7.1 `goto`

Navega a una URL.

**Parámetros:**
- `url` (string, requerido)

### 7.2 `click`

Hace click en un elemento de la página usando **movimiento real del ratón** (vía `invisible_playwright`), no un click directo de Playwright. El cursor se desplaza suavemente hasta el elemento y hace click, imitando el comportamiento humano.

**Parámetros:**
- `selector` (string, requerido) — selector CSS del elemento.

### 7.3 `fill`

Rellena un campo de texto. El ratón se mueve de forma realista hasta el campo (como en `click`), hace click en él, y luego escribe el texto caracter por caracter con delays variables, imitando tipeo humano. Todo mediante `invisible_playwright`.

**Parámetros:**
- `selector` (string, requerido)
- `value` (string, requerido)

### 7.4 `keystroke`

Envía una o más teclas (ej: Enter, Tab, Escape, combinaciones como Ctrl+A).

**Parámetros:**
- `keys` (string, requerido) — tecla o secuencia (formato Playwright `page.keyboard.press`).

### 7.5 `chain`

Ejecuta múltiples acciones en secuencia dentro de una misma llamada.

**Parámetros:**
- `steps` (array de objetos, requerido) — cada objeto tiene:
  - `tool` (string): nombre de la tool
  - `params` (object): parámetros de esa tool

La respuesta incluye un único diff agregado de toda la cadena.

### 7.6 `sleep`

Espera un tiempo o hasta que se cumpla una condición.

**Parámetros:**
- `seconds` (number, opcional)
- `wait_for_visible` (string, opcional) — selector CSS a esperar visible
- `wait_for_hidden` (string, opcional) — selector CSS a esperar oculto
- `timeout` (number, opcional) — timeout máximo en ms (por defecto 10000)

Si no se especifica ni `seconds` ni `wait_for_*`, se esperan 2 segundos por defecto.

### 7.7 `view`

Obtiene información de los elementos visibles en la página.

**Parámetros:**
- `selector` (string, opcional) — filter por CSS selector
- `id` (string, opcional) — filter por id
- `type` (string, opcional) — filter por tipo de elemento (button, input, a, img, etc.)
- `offset` (integer, opcional) — para paginación
- `limit` (integer, opcional, por defecto 50) — máximo de elementos a devolver

**Devuelve** para cada elemento: tag, id, clases, texto visible, href, src, value, aria-label, aria-role, bounding box.

### 7.8 Tab Tools

- `tab_list` — lista todas las tabs abiertas (id, título, url).
- `tab_new` — abre una nueva tab (parámetro: `url` opcional).
- `tab_switch` — cambia a una tab por su id.
- `tab_close` — cierra la tab actual o una específica (parámetro: `id` opcional).

### 7.9 `captcha_solve`

Resuelve un captcha usando el servicio 2captcha. Solo disponible si se proporcionó `--2captcha-api-key` al iniciar el servidor.

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `type` | string | sí | Tipo de captcha: `normal`, `text`, `recaptcha_v2`, `recaptcha_v3`, `funcaptcha`, `geetest`, `keycaptcha`, `capy`, `grid`, `canvas`, `click`, `rotate` |
| `sitekey` | string | para reCAPTCHA/FunCaptcha | Site key del captcha |
| `url` | string | para reCAPTCHA/FunCaptcha/GeeTest | URL de la página donde aparece el captcha |
| `image` | string | para normal/grid/canvas/click/rotate | Imagen del captcha en base64 |
| `text` | string | para text | Pregunta del captcha textual |
| `challenge` | string | para GeeTest | Challenge ID de GeeTest |
| `gt` | string | para GeeTest | GT de GeeTest |
| `version` | string | para recaptcha | `v2` (default) o `v3` |
| `action` | string | para recaptcha v3 | Action name |
| `min_score` | number | para recaptcha v3 | Score mínimo (0.0 - 1.0) |
| `proxy` | object | opcional | Proxy para resolver ({type, uri}) |

**Devuelve:**
- `result` (string) — token o texto resuelto
- `captcha_id` (string) — ID del captcha en 2captcha (para reportar)

La tool también expone dos sub-comandos:
- `captcha_report_good(captcha_id)` — reportar captcha bien resuelto
- `captcha_report_bad(captcha_id)` — reportar captcha mal resuelto

## 8. Mecanismo de Diff

- Antes de ejecutar la acción, se captura el HTML serializado del `<body>`.
- Después de la acción, se captura el nuevo HTML.
- Se calcula un diff textual utilizando una librería eficiente (difflib, google-diff-match-patch, o similar).
- El diff se devuelve como parte del resultado de la herramienta, permitiendo a la IA entender exactamente qué cambió sin tener que hacer un `view` completo.

**Formato del diff:** Representación unificada o estructurada (añadidos/eliminaciones/modificaciones). Pendiente de decidir en implementación cuál resulta más óptimo para los modelos.

## 9. Indetectabilidad

- Se usa `invisible_playwright` para aplicar parches que evitan detección como navigator.webdriver, detección de automatización, etc.
- Se aplica en la creación del contexto de navegador.
- `click` y `fill` usan movimiento real del ratón (no saltos directos) con curvas bezier y delays variables, implementados por `invisible_playwright`.
- `fill` escribe caracter por caracter con velocidad variable, no con `fill()` directo de Playwright.

## 10. Tests

- pytest como framework.
- Tests unitarios para el cálculo de diff.
- Tests de integración para cada tool (navegador real headless).
- Tests de sesión persistente.
- Tests de concurrencia (múltiples sesiones MCP simultáneas sin estado compartido).
- Tests de indetectabilidad (verificar navigator.webdriver, movimiento real de ratón).

## 11. No Funcionales

| Aspecto | Requisito |
|---|---|
| Rendimiento | El diff no debe añadir más de 500ms overhead |
| Portabilidad | Solo Linux vía Docker |
| Seguridad | Solo dentro del contenedor Docker |
| Mantenibilidad | Toolset pequeño, código modular, cada tool en su propio módulo |
| Aislamiento | Cada sesión MCP tiene su propio browser context de Playwright |
| Concurrencia | Soporte para N instancias de cliente MCP simultáneas sin estado compartido |

## 12. Hitos Tentativos

1. **v0.1**: Servidor MCP mínimo con `goto`, `click` (mouse real), `fill` (mouse real + tipeo humano), `keystroke` + diff + Docker.
2. **v0.2**: `view`, `sleep`, `chain`.
3. **v0.3**: Multi-instancia (browser context por sesión MCP) + tab tools.
4. **v0.4**: Tests completos (concurrencia, indetectabilidad, tools), pulido.
5. **v0.5**: Captcha tool + integración 2captcha.
6. **v1.0**: Release estable.
