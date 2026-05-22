import styles from './page.module.css';

export default function PiezaPage() {
  return (
    <div className={styles.root}>
      <header className={styles.header}>
        <h1 className={styles.title}>Mil Ojos</h1>
        <div className={styles.subtitle}>Manuel Mendoza <br/> Jóvenes creadores 2026 | Nuevas tecnologías</div>
        <p className={styles.introText}>
          Mil Ojos es una pieza de arte electrónico en forma de exoesqueleto equipado con nueve cámaras móviles distribuidas alrededor de la cabeza del portador. Cada cámara está montada sobre servomotores que le permiten moverse de forma independiente, girar y seguir objetos visuales. El sistema cuenta con un módulo de inteligencia artificial que compara en tiempo real los rostros detectados en el entorno con una base de datos de personas desaparecidas en México.
          <br/><br/>
          Esta obra parte de una imposibilidad humana: reconocer, retener y cotejar los cientos de rostros de personas desaparecidas que circulan diariamente en afiches, pantallas o redes sociales. La pieza actúa como una metáfora técnica de una memoria extendida, un cuerpo expandido que busca incansablemente entre la multitud. Cada cámara, cada servo, cada conexión de datos, se convierte en un ojo vigilante que no olvida, que insiste.
          <br/><br/>
          El proyecto propone una reflexión sobre el duelo colectivo, la vigilancia afectiva y la carga que implica la memoria social. La obra opera como un gesto poético y político que explora cómo el cuerpo puede ser habitado por la tecnología no como arma, sino como órgano de búsqueda.
        </p>
      </header>

      <div className={styles.contentContainer}>

        {/* Metáforas Técnicas */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Metáforas Técnicas</h2>
          <p className={styles.textBlock}>
            Esta sección documenta la relación simbiótica entre la arquitectura técnica del proyecto Mil Ojos y su carga conceptual. Aquí, el exoesqueleto no se entiende como una herramienta de optimización humana, sino como un cuerpo expandido por la necesidad de justicia. Cada elemento técnico es una respuesta a la "imposibilidad humana" de procesar la tragedia de la desaparición de forma individual, delegando en el algoritmo y el servomotor la tarea de la insistencia.
          </p>
          
          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemTitle}>Punto 1: Desmitificar a través de la Potencia Técnica</span>
              <span className={styles.itemDesc}>
                "Al hablar de desmitificar la tecnología en este proyecto, no busco simplificarla. Al contrario: presento la IA y la robótica como sistemas de una complejidad técnica profunda que aquí recuperan su potencial transformador. A menudo, las nuevas tecnologías se relegan a lo ornamental, pero en 'Mil Ojos', la arquitectura del software y el hardware está diseñada para una tarea crítica: la justicia. No es tecnología 'vacía'; es tecnología con agencia. Estamos desplazando el uso de algoritmos avanzados de los centros de control estatal para poner esa misma potencia técnica al servicio de una búsqueda humana y urgente."
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemTitle}>Punto 2: Vigilancia Afectiva (Hacia una nueva infraestructura)</span>
              <span className={styles.itemDesc}>
                "La vigilancia aquí no es un ejercicio de poder vertical, sino una infraestructura de cuidado. Al integrar cámaras y procesamiento en tiempo real, estamos hackeando el concepto de 'vigilancia' de David Lyon. Proponemos que la alta resolución y la velocidad de procesamiento sean las que sostengan la mirada cuando el ojo humano se agota. Es una vigilancia de alta precisión motivada por el afecto colectivo: una mirada que no juzga a la multitud, sino que la escanea con la esperanza técnica del hallazgo."
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemTitle}>Punto 3: Encarnación de la Memoria (La prótesis como expansión)</span>
              <span className={styles.itemDesc}>
                "Finalmente, abordamos la Encarnación de la Memoria. Aquí, el software de reconocimiento facial no es un accesorio, es una extensión cognitiva. Reconocemos que el volumen de la tragedia en México supera nuestra capacidad biológica de procesamiento. Por ello, recurrimos al potencial del 'machine learning' para crear un cuerpo expandido. El exoesqueleto se convierte en un órgano de búsqueda especializado: una prótesis técnica que permite que el portador encarne una memoria social incansable, capaz de procesar datos y rostros allí donde la memoria humana encontraría su límite."
              </span>
            </div>
          </div>

          <div className={styles.tableContainer}>
            <table className={styles.dataTable}>
              <thead>
                <tr>
                  <th>Componente Técnico</th>
                  <th>Concepto Metafórico</th>
                  <th>Dimensión Teórica Relacionada</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Nueve cámaras móviles</td>
                  <td>Cuerpo Expandido / Ojo Vigilante</td>
                  <td>La vigilancia como práctica de cuidado y afecto.</td>
                </tr>
                <tr>
                  <td>Servomotores independientes</td>
                  <td>Insistencia / Búsqueda Incansable</td>
                  <td>La memoria como un trabajo activo y persistente.</td>
                </tr>
                <tr>
                  <td>Módulo de IA (Comparación facial)</td>
                  <td>Memoria Extendida / Social</td>
                  <td>El duelo colectivo frente a la imposibilidad humana de retener rostros.</td>
                </tr>
                <tr>
                  <td>Exoesqueleto (Soporte)</td>
                  <td>Órgano de Búsqueda</td>
                  <td>La violencia inscrita y reorganizando el cuerpo cotidiano.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Estado del Arte */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Estado del Arte</h2>
          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Rafael Lozano-Hemmer (2015)</span>
              <span className={styles.itemTitle}>Nivel de Confianza</span>
              <span className={styles.itemDesc}>
                Es una instalación de arte creada tras la desaparición de los 43 estudiantes de Ayotzinapa. Utiliza algoritmos de reconocimiento facial (típicamente policiales) para buscar los rasgos de los estudiantes en el rostro del espectador. La obra subvierte la tecnología de vigilancia, transformándola en una herramienta de búsqueda y empatía que evidencia la imposibilidad del hallazgo y la persistencia del duelo.
                <br/><br/>
                Técnicamente, la pieza opera mediante una cámara que escanea al espectador y un algoritmo que busca coincidencias en una base de datos de los desaparecidos. Lo potente aquí es el fallo ético del algoritmo: el sistema siempre te dará un 'nivel de confianza' (un porcentaje), pero sabemos que es una búsqueda condenada al fracaso porque los estudiantes no están ahí. Es una métrica de la ausencia.
              </span>
            </div>

            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Stelarc</span>
              <span className={styles.itemTitle}>Extended Body: Prothetic Head and Third Ear</span>
              <span className={styles.itemDesc}>
                Artista de performance que considera que el cuerpo humano es biológicamente insuficiente para el entorno tecnológico actual. Propone que la tecnología no es algo ajeno, sino una extensión de nuestra estructura biológica.
                <br/><br/>
                En mi proyecto hago una torsión ética a este concepto:
                1. De la función a la responsabilidad: En 'Mil Ojos' el cuerpo se expande por una necesidad ética. El exoesqueleto no busca que el portador sea 'mejor', sino que sostenga la tarea de no olvidar.
                2. El Órgano de Búsqueda: Esta tecnología actúa como arquitectura anatómica que reorganiza al portador en un agente de memoria social.
                3. La Invasión de lo Ordinario: Esta extensión técnica ya no es experimento, sino forma de habitar lo cotidiano reconfigurado por la violencia.
              </span>
            </div>

            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Trevor Paglen (2017)</span>
              <span className={styles.itemTitle}>Operational Images</span>
              <span className={styles.itemDesc}>
                Artista y geógrafo que investiga las infraestructuras de vigilancia masiva y sistemas de IA. Su concepto de "imágenes operacionales" se refiere a imágenes hechas por máquinas para otras máquinas.
                <br/><br/>
                En 'Mil Ojos', invertimos la invisibilidad: materializamos el proceso de escaneo algorítmico para que la sociedad no pueda ignorarlo. La IA aquí es evidencia, no secreto. Traducimos el lenguaje abstracto de los datos a un gesto corporal de búsqueda constante.
              </span>
            </div>

            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Oscar Muñoz (2004-2005)</span>
              <span className={styles.itemTitle}>Proyecto para un memorial</span>
              <span className={styles.itemDesc}>
                Artista que explora la fragilidad de la imagen y la memoria. Muñoz utiliza agua para dibujar rostros sobre piedra caliente; la imagen se evapora, obligándolo a dibujarla una y otra vez.
                <br/><br/>
                Mis servomotores representan una voluntad mecánica que no acepta la ausencia. El movimiento independiente de las cámaras es una acción infinita para que el rostro no se desvanezca en el olvido social, asumiendo el duelo como un trabajo activo que la memoria biológica ya no puede sostener sola.
              </span>
            </div>

            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Lynn Hershman Leeson</span>
              <span className={styles.itemTitle}>The Cyborg Series</span>
              <span className={styles.itemDesc}>
                Pionera del arte mediático que explora cómo la mirada tecnológica atraviesa el cuerpo femenino y redefine la identidad. En 'Mil Ojos', el exoesqueleto es una 'interfaz de búsqueda' que diluye la frontera entre portador y sistema, devolviendo el control al ciudadano que decide portar la memoria de los ausentes.
              </span>
            </div>
          </div>
        </section>

        {/* Bibliografía */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Bibliografía</h2>
          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Judith Butler (2006)</span>
              <span className={styles.itemTitle}>Vida precaria. El poder del duelo y la violencia</span>
              <span className={styles.itemDesc}>
                Este libro reflexiona sobre el duelo como una experiencia política y colectiva, cuestionando qué vidas son consideradas dignas de ser lloradas y recordadas. Butler propone que el duelo público revela estructuras de poder, exclusión y reconocimiento, lo que permite pensar la desaparición forzada como una forma de violencia que suspende el cierre del duelo y exige memoria persistente.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Mgte. Isaac Vargas (2022)</span>
              <span className={styles.itemTitle}>Más que un expediente… Las madres de las personas desaparecidas en México y sus carpetas de investigación</span>
              <span className={styles.itemDesc}>
                Este artículo analiza la carpeta de investigación no solo como un documento burocrático, sino como un artefacto simbólico que contiene la “promesa de justicia” y cumple un papel social importante.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Elizabeth Jelin (2002)</span>
              <span className={styles.itemTitle}>Los trabajos de la memoria</span>
              <span className={styles.itemDesc}>
                Jelin analiza la memoria como un proceso activo, conflictivo y situado, especialmente en contextos de violencia política y desaparición. Introduce la idea de la memoria como trabajo insistente, sostenido por colectivos que se niegan al olvido.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Veena Das (2007)</span>
              <span className={styles.itemTitle}>Life and Words: Violence and the Descent into the Ordinary</span>
              <span className={styles.itemDesc}>
                Das explora cómo la violencia extrema se inscribe en la vida cotidiana y en prácticas aparentemente ordinarias. Su trabajo permite pensar la desaparición no solo como evento excepcional, sino como una presencia constante que reorganiza afectos, cuerpos y rutinas.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>David Lyon (2007)</span>
              <span className={styles.itemTitle}>Surveillance Studies</span>
              <span className={styles.itemDesc}>
                Lyon ofrece un marco teórico para comprender la vigilancia como una práctica social amplia, más allá del control policial o estatal. Este enfoque permite resignificar la vigilancia como una práctica que también puede estar cargada de afectos, cuidados y responsabilidades colectivas.
              </span>
            </div>
          </div>
        </section>

        {/* Conexiones */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Conexiones (Hardware & Software)</h2>
          <div className={styles.tableContainer}>
            <table className={styles.dataTable}>
              <thead>
                <tr>
                  <th>Sistema</th>
                  <th>Componentes Clave</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Visión</td>
                  <td>9x Waveshare ESP32-S3 ETH + Cámaras OV2640.</td>
                </tr>
                <tr>
                  <td>Movimiento</td>
                  <td>18x Servos (9 Pan / 9 Tilt) + Estructuras Pan-Tilt.</td>
                </tr>
                <tr>
                  <td>Red</td>
                  <td>2x MikroTik hEX S + Cables Ethernet Planos.</td>
                </tr>
                <tr>
                  <td>Procesamiento</td>
                  <td>Mini Brick PC + SSD (Base de datos local).</td>
                </tr>
                <tr>
                  <td>Energía</td>
                  <td>Batería LiPo + 3 Buck Converters (PC, Lógica, Servos).</td>
                </tr>
                <tr>
                  <td>Interfaz</td>
                  <td>Buzzer/Audio + Anillos LED + Kill Switch.</td>
                </tr>
                <tr>
                  <td>Clima</td>
                  <td>Ventiladores DC + Disipadores de calor.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </div>
    </div>
  );
}
