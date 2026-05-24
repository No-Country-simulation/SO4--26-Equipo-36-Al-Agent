# Especificación Técnica de Habilidad
**Código de Skill:** SKL-FE-DSGN-001  
**Versión:** 1.0.0  
**Estándar:** ISO/IEC 26514 / Agile DoD  

---

### 1. Ficha de Identificación del Skill

| Atributo | Definición Técnica |
| --- | --- |
| **Habilidad Principal** | Diseño y Desarrollo Frontend de Alto Nivel |
| **Objetivo de Dominio** | Capacitar en la creación de interfaces frontend distintivas y de nivel de producción que eviten la estética genérica de "IA", implementando diseños atrevidos y código funcional altamente refinado. |
| **Tipo de Proyecto** | Desarrollo Frontend / UI-UX Engineering |
| **Complejidad** | Media/Alta |

---

### 2. Descripción y Filosofía de Diseño

El skill de **Diseño Frontend** se centra en la creación creativa y la implementación técnica de interfaces gráficas. Este enfoque busca romper con la monotonía estética mediante elecciones de diseño con propósito, evitando a toda costa la denominada "estética IA" (fuentes genéricas, gradientes morados sobre blanco, layouts predecibles).

* **Intencionalidad Estética:** Elegir una dirección de diseño clara (minimalismo brutalista, caos maximalista, utilitario industrial, etc.) y ejecutarla con precisión.
* **Componentización:** Construcción de interfaces basadas en componentes reutilizables, cohesivos y mantenibles (usando HTML/CSS, React, Vue, o TailwindCSS/DaisyUI).
* **Armonía y Contraste:** Uso de paletas de colores dominantes con acentos fuertes, emparejamientos tipográficos con carácter y dominio de la composición espacial (asimetría, superposición, etc.).
* **Fidelidad y Perfección:** Cada detalle, desde los márgenes (padding/margin) hasta el comportamiento en hover, debe estar pulido. La elegancia se deriva de una ejecución perfecta de la visión inicial.

---

### 3. Requerimientos del Skill

#### 3.1. Requerimientos Funcionales (RF)
* **[RF-01] Coherencia Temática:** El diseño debe mantener una paleta de colores cohesiva y un esquema tipográfico utilizando variables CSS (`--primary-color`, `--font-main`, etc.) o los tokens del framework utilizado.
* **[RF-02] Responsividad:** Todos los componentes e interfaces deben adaptarse fluidamente desde dispositivos móviles hasta pantallas ultra-anchas.
* **[RF-03] Microinteracciones:** Inclusión de animaciones y transiciones (idealmente solo CSS) para efectos de estado (hover, active, focus) y cargas de página con retrasos escalonados (staggered reveals).

#### 3.2. Requerimientos No Funcionales (RNF)
* **[RNF-01] Identidad Visual:** El diseño debe tener un punto de vista estético claro, atrevido e inolvidable.
* **[RNF-02] Rendimiento:** Las animaciones y sombras no deben causar caídas en los FPS durante el renderizado del navegador.
* **[RNF-03] Accesibilidad:** Cumplimiento de estándares básicos de contraste y navegación amigable para usuarios con diferentes capacidades visuales o motoras (WCAG básico).

---

### 4. Criterios de Aceptación (Definition of Done)

Se considera que la aplicación de este skill es exitosa si:
* **Fidelidad Visual:** El código renderiza una interfaz que luce premium y se aleja diametralmente de los patrones visuales por defecto o clisés corporativos.
* **Calidad Técnica:** El código HTML/CSS/JS es limpio, modular, de grado de producción y se integra sin errores.
* **Experiencia de Usuario (UX):** La interfaz comunica claramente su propósito e incluye detalles que deleitan al usuario final (ej. cursores personalizados, efectos de scroll, texturas).

---

### 5. Ecosistema de Herramientas (Stack)

* **Lenguajes:** HTML5 Semántico, CSS3 Moderno (Grid, Flexbox, Variables), JavaScript (ES6+).
* **Frameworks/Librerías:** TailwindCSS, DaisyUI, React o Vue (dependiendo del requerimiento técnico).
* **Tipografía y Assets:** Google Fonts (opciones no convencionales), bibliotecas de iconos SVG.

---

### 6. Metodología de Práctica (Paso a Paso)

1. **Fase de Contexto y Decisión (Design Thinking):** Antes de tirar código, define el **propósito** (¿quién lo usa y para qué?), el **tono** (minimalista, retro, maximalista) y las **restricciones**. Decide qué hará que este diseño sea inolvidable.
2. **Fase de Setup de Tokens:** Define las variables CSS (colores, fuentes, espacios) o configura el `tailwind.config.js` para asegurar coherencia en todo el desarrollo.
3. **Fase de Maquetado Estructural:** Crea la estructura semántica en HTML asegurando un flujo natural del documento.
4. **Fase de Estilizado y Refinamiento:** Aplica la dirección estética, prestando especial atención a tipografía, jerarquía visual, espaciado negativo e interacción.
5. **Fase de Pulido:** Añade detalles visuales extra: texturas de ruido, gradientes, animaciones escalonadas de entrada, y prueba la responsividad.

---

### 7. Antipatrones (Lo que NO se debe hacer)

* ⚠️ **[Antipatrón 1] El Síndrome de Arial/Inter:** Utilizar fuentes tipográficas sobre-usadas por defecto en lugar de combinaciones con carácter (ej. una tipografía Display llamativa combinada con un cuerpo de texto serif elegante).
* ⚠️ **[Antipatrón 2] El Estilo "IA Genérico":** Abusar de gradientes morado/rosa sobre fondo blanco brillante asumiendo que "parece moderno".
* ⚠️ **[Antipatrón 3] Composición Tímida:** Repartir equitativamente el peso visual, evitando contrastes fuertes. Un diseño audaz requiere jerarquías extremas.
* ⚠️ **[Antipatrón 4] Diseño sin Contexto:** Aplicar un tema de "ciberpunk" a un portal médico institucional. El atrevimiento estético debe alinearse y empatizar con el propósito del proyecto.

---

### 8. Evaluación y KPIs

| Métrica | Meta |
| --- | --- |
| **Puntaje de Rendimiento (Lighthouse/PageSpeed)** | > 90 en Accesibilidad y Rendimiento visual |
| **Tiempo de Respuesta a Interacciones** | < 100ms para asegurar fluidez |
| **Cumplimiento Estético** | Clara diferenciación de plantillas estándar |

---

### 9. Arquitectura y Buenas Prácticas de Grado Industrial

#### 9.1. Composición y Espacio
* **Romper el Grid de Forma Controlada:** Usar asimetrías, flujos diagonales y elementos que se superponen (Z-index layering) en lugar de encajar todo rígidamente en bloques.
* **Espacio Negativo vs. Densidad:** El espacio en blanco masivo denota lujo y claridad. La alta densidad bien estructurada (tipo dashboard industrial) transmite control y funcionalidad masiva. Ambas son válidas si son intencionales.

#### 9.2. Color y Textura
* **Dominancia y Acento:** Implementar la regla 60/30/10 en el color o apostar por esquemas monocromáticos hiper-contrastados.
* **Profundidad:** Evitar los fondos planos de color puro si el tema lo permite. Añadir mallas de gradiente (gradient meshes), patrones geométricos sutiles o sobreposiciones de texturas tipo grano/ruido (noise texture) para darle vida a la interfaz.

#### 9.3. Movimiento y Deleite
* **Animaciones de Alta Impacto:** Una sola animación orquestada (ej. elementos que aparecen secuencialmente al cargar la página mediante `animation-delay` en CSS) es mejor que 20 micro-interacciones dispersas sin sentido.
* **Interacciones Táctiles en Escritorio:** El uso creativo del hover (crecimiento sutil, cambio dramático de color, revelación de elementos) convierte una web aburrida en una experiencia exploratoria.

---

### 10. Recursos y Documentación Oficial

* [Tailwind CSS Documentation](https://tailwindcss.com/docs)
* [DaisyUI Components](https://daisyui.com/)
* [Awwwards - Inspiración Frontend](https://www.awwwards.com/)
