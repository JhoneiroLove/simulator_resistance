"""
Servicio para lógica de negocio relacionada con sitios de infección.
Contiene cálculos de penetración de antibióticos y ajustes ambientales.
"""

class InfectionSiteService:
    """Servicio con métodos estáticos para cálculos relacionados con sitios de infección."""

    @staticmethod
    def calcular_penetracion_antibiotico(infection_site, antibiotico):
        """
        Calcula el factor de penetración del antibiótico en el sitio de infección.

        La penetración depende de:
        1. Perfusión sanguínea del sitio (principal factor)
        2. Tipo de antibiótico y sus propiedades fisicoquímicas
        3. Características del sitio (barrera hematoencefálica, biofilms, etc.)

        Args:
            infection_site: Instancia del modelo InfectionSite
            antibiotico: Diccionario con datos del antibiótico que incluye:
                        - 'tipo': tipo de antibiótico (str)
                        - 'nombre': nombre del antibiótico (str)

        Returns:
            float: Factor de penetración entre 0.0 y 1.0
                   - 1.0: Penetración completa (100% de concentración alcanza el sitio)
                   - 0.5: Penetración moderada (50% de concentración alcanza el sitio)
                   - 0.0: Penetración nula (antibiótico no llega al sitio)

        Uso:
            concentracion_efectiva = concentracion_sistemica * factor_penetracion

        Ejemplos:
            - Torrente sanguíneo + Meropenem: 0.95 (excelente penetración)
            - SNC + Ciprofloxacino: 0.40 (moderada, barrera hematoencefálica)
            - Hueso + Colistina: 0.20 (baja penetración ósea)
        """
        # Factor base: perfusión sanguínea del sitio
        factor_base = infection_site.perfusion_sanguinea

        # Ajustes según tipo de antibiótico y sitio
        tipo_antibiotico = antibiotico.get("tipo", "").lower()
        nombre_sitio = infection_site.nombre.lower()

        # Modificador según características del sitio
        modificador = 1.0

        # Sistema Nervioso Central - Barrera hematoencefálica
        if (
            "liquido_cefalorraquideo" in nombre_sitio
            or "snc" in nombre_sitio
            or "cerebro" in nombre_sitio
        ):
            modificador = InfectionSiteService._get_cns_penetration_modifier(
                tipo_antibiotico
            )

        # Hueso y articulaciones - Baja vascularización
        elif "hueso" in nombre_sitio or "articulaciones" in nombre_sitio:
            modificador = InfectionSiteService._get_bone_penetration_modifier(
                tipo_antibiotico
            )

        # Córnea - Estructura avascular
        elif "cornea" in nombre_sitio or "ojo" in nombre_sitio:
            modificador = InfectionSiteService._get_eye_penetration_modifier(
                tipo_antibiotico
            )

        # Pulmón - Buena perfusión pero puede haber biofilms
        elif "pulmon" in nombre_sitio or "respiratorio" in nombre_sitio:
            modificador = InfectionSiteService._get_lung_penetration_modifier(
                tipo_antibiotico
            )

        # Torrente sanguíneo - Acceso directo
        elif "sangre" in nombre_sitio or "torrente" in nombre_sitio:
            modificador = 1.0  # Penetración máxima

        # Heridas - Penetración reducida por daño tisular
        elif "herida" in nombre_sitio or "quemadura" in nombre_sitio:
            modificador = 0.7  # Tejido dañado reduce penetración

        # Tracto urinario - Buena excreción renal
        elif "orina" in nombre_sitio or "urinario" in nombre_sitio:
            modificador = InfectionSiteService._get_urinary_penetration_modifier(
                tipo_antibiotico
            )

        # Calcular factor final
        factor_penetracion = factor_base * modificador

        # Asegurar que esté en el rango [0.0, 1.0]
        return min(1.0, max(0.0, factor_penetracion))

    @staticmethod
    def _get_cns_penetration_modifier(tipo_antibiotico):
        """
        Modificador de penetración para Sistema Nervioso Central.
        Fuente: Guías de meningitis bacteriana, estudios farmacocinéticos.
        """
        penetracion_snc = {
            "carbapenémico": 0.5,  # Buena penetración (Meropenem)
            "fluoroquinolona": 0.6,  # Excelente penetración
            "cefalosporina": 0.6,  # Buena (Ceftriaxona, Cefotaxima)
            "polimixina": 0.1,  # Muy pobre penetración
            "aminoglucósido": 0.1,  # No cruza bien la barrera
            "penicilina": 0.4,  # Moderada
            "glicilciclina": 0.2,  # Pobre penetración
        }
        return penetracion_snc.get(tipo_antibiotico, 0.3)

    @staticmethod
    def _get_bone_penetration_modifier(tipo_antibiotico):
        """
        Modificador de penetración para hueso y articulaciones.
        Fuente: Guías de osteomielitis.
        """
        penetracion_hueso = {
            "carbapenémico": 0.4,
            "fluoroquinolona": 0.9,  # Excelente para hueso (gold standard)
            "cefalosporina": 0.5,
            "polimixina": 0.2,
            "aminoglucósido": 0.3,
            "penicilina": 0.5,
            "glicilciclina": 0.7,  # Buena penetración ósea
        }
        return penetracion_hueso.get(tipo_antibiotico, 0.4)

    @staticmethod
    def _get_eye_penetration_modifier(tipo_antibiotico):
        """
        Modificador de penetración para córnea y estructuras oculares.
        Fuente: Guías de endoftalmitis y queratitis.
        """
        penetracion_ojo = {
            "carbapenémico": 0.3,
            "fluoroquinolona": 0.8,  # Excelente para infecciones oculares
            "cefalosporina": 0.4,
            "polimixina": 0.5,  # Uso tópico principalmente
            "aminoglucósido": 0.6,  # Bueno para uso tópico
            "penicilina": 0.3,
            "glicilciclina": 0.2,
        }
        return penetracion_ojo.get(tipo_antibiotico, 0.4)

    @staticmethod
    def _get_lung_penetration_modifier(tipo_antibiotico):
        """
        Modificador de penetración para tejido pulmonar.
        Fuente: Guías de neumonía nosocomial.
        """
        penetracion_pulmon = {
            "carbapenémico": 0.8,
            "fluoroquinolona": 0.9,  # Excelente concentración pulmonar
            "cefalosporina": 0.7,
            "polimixina": 0.6,
            "aminoglucósido": 0.5,  # Menor penetración en tejido
            "penicilina": 0.7,
            "glicilciclina": 0.9,  # Excelente penetración pulmonar
        }
        return penetracion_pulmon.get(tipo_antibiotico, 0.7)

    @staticmethod
    def _get_urinary_penetration_modifier(tipo_antibiotico):
        """
        Modificador de penetración para tracto urinario.
        Fuente: Guías de ITU complicada.
        """
        penetracion_urinaria = {
            "carbapenémico": 0.9,
            "fluoroquinolona": 1.0,  # Excreción renal excelente
            "cefalosporina": 0.8,
            "polimixina": 0.7,
            "aminoglucósido": 1.0,  # Excelente excreción renal
            "penicilina": 0.9,
            "glicilciclina": 0.6,
        }
        return penetracion_urinaria.get(tipo_antibiotico, 0.8)

    @staticmethod
    def get_ph_modifier(sitio_ph, antibiotico_tipo):
        """
        Calcula el modificador de actividad del antibiótico según el pH del sitio.

        Algunos antibióticos son más activos en pH ácido, otros en pH alcalino.

        Args:
            sitio_ph (float): pH del sitio de infección
            antibiotico_tipo (str): Tipo de antibiótico

        Returns:
            float: Modificador de actividad (0.5 a 1.2)
                   - 1.0: pH óptimo
                   - >1.0: pH favorece la actividad
                   - <1.0: pH reduce la actividad
        """
        # pH óptimo para cada tipo de antibiótico
        ph_optimos = {
            "aminoglucósido": 7.8,  # Más activos en pH alcalino
            "fluoroquinolona": 7.0,  # Neutro
            "carbapenémico": 7.4,  # Ligeramente alcalino
            "penicilina": 7.0,  # Neutro
            "cefalosporina": 7.2,  # Ligeramente alcalino
            "polimixina": 7.5,  # Alcalino
            "glicilciclina": 7.4,  # Fisiológico
        }

        ph_optimo = ph_optimos.get(antibiotico_tipo.lower(), 7.4)

        # Calcular desviación del pH óptimo
        desviacion = abs(sitio_ph - ph_optimo)

        # Penalización por desviación del pH
        # Cada 0.5 unidades de desviación reduce actividad en 10%
        penalizacion = desviacion * 0.2

        # Modificador entre 0.5 (muy desviado) y 1.0 (pH óptimo)
        modificador = max(0.5, 1.0 - penalizacion)

        return round(modificador, 2)

    @staticmethod
    def get_capacity_utilization(poblacion_actual, capacidad_carga):
        """
        Calcula el porcentaje de utilización de la capacidad de carga del sitio.

        Args:
            poblacion_actual (float): Población bacteriana actual
            capacidad_carga (float): Capacidad de carga del sitio (K)

        Returns:
            float: Porcentaje de utilización (0.0 a 1.0)
        """
        if capacidad_carga <= 0:
            return 1.0

        utilizacion = poblacion_actual / capacidad_carga
        return min(1.0, max(0.0, utilizacion))

    @staticmethod
    def get_site_severity_category(nombre_sitio):
        """
        Categoriza la severidad de la infección según el sitio.

        Args:
            nombre_sitio (str): Nombre del sitio de infección

        Returns:
            str: Categoría de severidad ('leve', 'moderada', 'grave', 'critica')
        """
        nombre = nombre_sitio.lower()

        # Infecciones críticas
        if any(
            keyword in nombre
            for keyword in [
                "sangre",
                "torrente",
                "sepsis",
                "liquido_cefalorraquideo",
                "snc",
                "meningitis",
            ]
        ):
            return "critica"

        # Infecciones graves
        if any(
            keyword in nombre
            for keyword in [
                "pulmon",
                "neumonia",
                "hueso",
                "osteomielitis",
                "endocardio",
            ]
        ):
            return "grave"

        # Infecciones moderadas
        if any(
            keyword in nombre
            for keyword in ["herida", "quemadura", "abdomen", "intraabdominal"]
        ):
            return "moderada"

        # Infecciones leves
        return "leve"