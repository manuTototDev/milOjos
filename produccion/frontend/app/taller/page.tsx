import Image from 'next/image';
import styles from './page.module.css';

export default function TallerPage() {
  return (
    <div className={styles.root}>
      <header className={styles.header}>
        <h1 className={styles.title}>Taller: Mil Ojos</h1>
        <div className={styles.subtitle}>Manuel Mendoza | Jóvenes creadores 2026</div>
        <p className={styles.introText}>
          Mil Ojos es una pieza de arte electrónico en forma de exoesqueleto equipado con nueve cámaras móviles distribuidas alrededor de la cabeza del portador. El sistema cuenta con un módulo de inteligencia artificial que compara en tiempo real los rostros detectados con una base de datos de personas desaparecidas en México.
          <br/><br/>
          Este taller está diseñado para ofrecer una reflexión crítica y técnica sobre cómo las tecnologías de reconocimiento facial pueden ser utilizadas como herramientas de memoria colectiva y búsqueda, transformando el control y la vigilancia en infraestructuras de afecto y justicia.
        </p>
      </header>

      <div className={styles.contentContainer}>
        
        {/* Datos Generales */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Datos Generales</h2>
          <div className={styles.detailsGrid}>
            <div className={styles.detailItem}>
              <span className={styles.detailLabel}>Fecha Propuesta</span>
              <span className={styles.detailValue}>13 de mayo de 2026</span>
            </div>
            <div className={styles.detailItem}>
              <span className={styles.detailLabel}>Horario</span>
              <span className={styles.detailValue}>15:00 a 17:00 hrs</span>
            </div>
            <div className={styles.detailItem}>
              <span className={styles.detailLabel}>Duración</span>
              <span className={styles.detailValue}>2 horas</span>
            </div>
            <div className={styles.detailItem}>
              <span className={styles.detailLabel}>Cupo Máximo</span>
              <span className={styles.detailValue}>20 personas</span>
            </div>
            <div className={styles.detailItem}>
              <span className={styles.detailLabel}>Costo</span>
              <span className={styles.detailValue}>Gratuito (Retribución Social)</span>
            </div>
          </div>
        </section>

        {/* MÓDULO 1: TEORÍA Y JUSTICIA SOCIAL */}
        <section className={styles.section}>
          <div className={styles.moduleHeader}>
            <span className={styles.moduleTime}>30 MIN</span>
            <h2 className={styles.moduleTitle}>1. Teoría y Justicia Social</h2>
          </div>
          <p className={styles.textBlock}>
            Análisis de la mirada tecnológica y el duelo colectivo. ¿Cómo el cuerpo puede ser habitado por la tecnología no como arma, sino como órgano de búsqueda?
          </p>

          <h3 className={styles.subTitle}>Contexto: La Magnitud de la Crisis</h3>
          <div className={styles.itemList}>
            <div className={styles.itemCard} style={{ borderLeftColor: 'var(--accent)', background: 'rgba(255, 45, 45, 0.05)' }}>
              <span className={styles.itemAuthor}>Registro Nacional (RNPDNO) - Marzo 2026</span>
              <span className={styles.itemTitle}>Más de 132,000 Personas Desaparecidas</span>
              <span className={styles.itemDesc}>
                México enfrenta una crisis humanitaria sin precedentes con más de 132,530 personas oficialmente registradas como desaparecidas y no localizadas. La magnitud del problema (sumada a decenas de miles de cuerpos no identificados en la crisis forense) supera la capacidad de procesamiento del Estado, generando un colapso en los mecanismos tradicionales de búsqueda.
                <br/><br/>
                Ante este desbordamiento numérico —la auténtica "imposibilidad humana" de recordar cada rostro—, "Mil Ojos" plantea la necesidad de delegar la memoria y el rastreo en una arquitectura algorítmica capaz de retener y cotejar a estos miles de ausentes de forma simultánea e incansable.
              </span>
            </div>
          </div>

          <h3 className={styles.subTitle}>Marco Teórico y Bibliografía</h3>
          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Judith Butler (2006)</span>
              <span className={styles.itemTitle}>Vida precaria. El poder del duelo y la violencia</span>
              <span className={styles.itemDesc}>
                Butler cuestiona qué vidas son consideradas dignas de ser lloradas y recordadas. La desaparición forzada suspende el cierre del duelo y exige una memoria persistente, lo cual nos lleva a la necesidad de "Mil Ojos" como herramienta frente a la incapacidad biológica del duelo ante cifras masivas.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Mgte. Isaac Vargas (2022)</span>
              <span className={styles.itemTitle}>Más que un expediente...</span>
              <span className={styles.itemDesc}>
                La carpeta de investigación como artefacto simbólico. De la burocracia estatal al gesto activo de la IA de mantener el expediente "abierto y buscando".
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Elizabeth Jelin (2002)</span>
              <span className={styles.itemTitle}>Los trabajos de la memoria</span>
              <span className={styles.itemDesc}>
                Jelin analiza la memoria como un proceso activo, conflictivo y situado. Introduce la idea de la memoria como un 'trabajo insistente' que no puede quedarse estático, lo que se traduce directamente en la repetición mecánica de los motores de la pieza.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>David Lyon (2007) / Veena Das (2007)</span>
              <span className={styles.itemTitle}>Vigilancia y la Invasión de lo Ordinario</span>
              <span className={styles.itemDesc}>
                Resignificar la vigilancia más allá del control policial, convirtiéndola en una práctica cargada de afectos y responsabilidades colectivas cuando la violencia extrema se inscribe y reorganiza las rutinas de la vida cotidiana.
              </span>
            </div>
          </div>

          <h3 className={styles.subTitle}>Estado del Arte / Referentes</h3>
          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Rafael Lozano-Hemmer (2015)</span>
              <span className={styles.itemTitle}>Nivel de Confianza</span>
              <span className={styles.itemDesc}>
                Uso de algoritmos faciales para buscar a los 43 estudiantes de Ayotzinapa. "Mil Ojos" toma esta genealogía: usar el porcentaje de coincidencia no como control, sino como métrica de la ausencia y la imposibilidad del hallazgo.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Oscar Muñoz (2004-2005)</span>
              <span className={styles.itemTitle}>Proyecto para un memorial</span>
              <span className={styles.itemDesc}>
                El acto incansable de intentar retener la presencia de quien ha sido borrado. Los servomotores de "Mil Ojos" son el equivalente tecnológico al pincel de agua de Muñoz: una acción que se repite infinitamente para que el rostro no termine de desvanecerse.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Lynn Hershman Leeson</span>
              <span className={styles.itemTitle}>The Cyborg Series</span>
              <span className={styles.itemDesc}>
                Pionera del arte mediático que explora cómo la mirada tecnológica atraviesa la identidad. En "Mil Ojos", el exoesqueleto funciona como interfaz que diluye la frontera humano/máquina, devolviendo el control de la vigilancia a los portadores de la memoria.
              </span>
            </div>
          </div>
        </section>

        {/* MÓDULO 2: ANATOMÍA DEL SISTEMA */}
        <section className={styles.section}>
          <div className={styles.moduleHeader}>
            <span className={styles.moduleTime}>45 MIN</span>
            <h2 className={styles.moduleTitle}>2. Anatomía del Sistema</h2>
          </div>
          <p className={styles.textBlock}>
            Desglose del hardware (ESP32-S3) y la lógica de visión de Mil Ojos. Desmitificando la robótica: no es tecnología vacía ni ornamental, está diseñada para una tarea crítica de justicia.
          </p>

          <div className={styles.mediaSection}>
            <div className={styles.imageWrapper}>
              <Image src="/milojos1.png" alt="Prototipo Mil Ojos" fill className={styles.image} />
            </div>
            <div className={styles.imageWrapper}>
              <Image src="/milojos2.png" alt="Prototipo Mil Ojos Detalle" fill className={styles.image} />
            </div>
          </div>

          <h3 className={styles.subTitle}>Metáforas del Hardware</h3>
          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemTitle}>Nueve Cámaras Móviles: "El Cuerpo Expandido"</span>
              <span className={styles.itemDesc}>
                Visión de 360 grados que elimina los puntos ciegos. El "Ojo Vigilante" se desprende de la mirada panóptica del Estado y se convierte en una infraestructura de cuidado que acompaña y no ignora lo que sucede en los márgenes biológicos.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemTitle}>Servomotores Independientes: "La Insistencia"</span>
              <span className={styles.itemDesc}>
                La memoria como un 'trabajo activo' (Jelin). Mientras el cansancio físico nos obliga a bajar la mirada, el servomotor sostiene la búsqueda mecánicamente, convirtiendo la fatiga del duelo en acción inagotable.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemTitle}>El Exoesqueleto: "El Órgano de Búsqueda"</span>
              <span className={styles.itemDesc}>
                Una torsión ética al concepto de Stelarc. No rediseñamos el cuerpo para ser "mejores", sino para ser capaces de sostener una tarea humanamente imposible. Es la manifestación física de cómo la violencia reorganiza el cuerpo para rastrear.
              </span>
            </div>
          </div>

          <h3 className={styles.subTitle}>Hardware y Conexiones</h3>
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
                  <td>9x Waveshare ESP32-S3 ETH + Cámaras OV2640</td>
                </tr>
                <tr>
                  <td>Movimiento</td>
                  <td>18x Servos (9 Pan / 9 Tilt) + Estructuras Pan-Tilt</td>
                </tr>
                <tr>
                  <td>Red / Energía</td>
                  <td>MikroTik hEX S + Batería LiPo + Buck Converters (PC, Lógica, Servos)</td>
                </tr>
                <tr>
                  <td>Procesamiento Local</td>
                  <td>Mini Brick PC + SSD para la base de datos off-grid</td>
                </tr>
                <tr>
                  <td>Interfaz y Clima</td>
                  <td>Anillos LED, Buzzer de alertas, Ventiladores DC y Kill Switch de emergencia</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* MÓDULO 3: SOFTWARE Y DATOS */}
        <section className={styles.section}>
          <div className={styles.moduleHeader}>
            <span className={styles.moduleTime}>30 MIN</span>
            <h2 className={styles.moduleTitle}>3. Software y Datos</h2>
          </div>
          <p className={styles.textBlock}>
            Funcionamiento de la base de datos de búsqueda y procesamiento de vectores faciales. Hackeando la vigilancia a favor de la memoria social.
          </p>

          <div className={styles.itemList}>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Módulo de IA (Comparación Facial)</span>
              <span className={styles.itemTitle}>La Memoria Extendida</span>
              <span className={styles.itemDesc}>
                El algoritmo coteja miles de rostros contra una base de datos en milisegundos. La IA no sustituye la empatía, actúa como una prótesis social que retiene los rostros ausentes ante la "imposibilidad del duelo".
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Trevor Paglen / Imágenes Operacionales</span>
              <span className={styles.itemTitle}>Invertir la invisibilidad</span>
              <span className={styles.itemDesc}>
                Paglen denuncia cómo el Estado usa la IA como 'caja negra'. En 'Mil Ojos', el exoesqueleto es ruidoso y evidente. Hacemos visible la infraestructura para devolver la visibilidad a quienes el sistema ha intentado borrar.
              </span>
            </div>
            <div className={styles.itemCard}>
              <span className={styles.itemAuthor}>Reconocimiento Facial</span>
              <span className={styles.itemTitle}>Vigilancia Afectiva</span>
              <span className={styles.itemDesc}>
                Una vigilancia de alta precisión motivada por el afecto. La mirada no juzga a la multitud, sino que la escanea con la esperanza técnica del hallazgo.
              </span>
            </div>
          </div>
        </section>

        {/* MÓDULO 4: CIERRE Y DEMOSTRACIÓN */}
        <section className={styles.section}>
          <div className={styles.moduleHeader}>
            <span className={styles.moduleTime}>15 MIN</span>
            <h2 className={styles.moduleTitle}>4. Cierre y Demostración</h2>
          </div>
          <p className={styles.textBlock} style={{ marginBottom: '1rem' }}>
            Diálogo abierto sobre soberanía tecnológica, agencias algorítmicas y visualización del sistema de hardware + software de "Mil Ojos" operando en un entorno local.
          </p>

          <div className={styles.videoSection}>
            <iframe 
              className={styles.video}
              src="https://www.youtube.com/embed/_3OxWfsQgJw?si=e2IPpr7rJaSS_K9x" 
              title="Demostración Mil Ojos" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
              referrerPolicy="strict-origin-when-cross-origin" 
              allowFullScreen>
            </iframe>
          </div>
        </section>

      </div>
    </div>
  );
}
