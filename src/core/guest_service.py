"""
Servicio para lógica de negocio relacionada con huéspedes/pacientes.
Contiene cálculos de función renal, hepática y modificadores para simulaciones.
"""

class GuestService:
    """Servicio con métodos estáticos para cálculos relacionados con pacientes."""
    
    @staticmethod
    def calcular_clearance_creatinina(age, weight, sex, creatinina_serica):
        """
        Calcula el clearance de creatinina usando la fórmula de Cockcroft-Gault.
        
        Fórmula de Cockcroft-Gault:
        CrCl (mL/min) = [(140 - edad) × peso (kg) × factor_sexo] / [72 × creatinina sérica (mg/dL)]
        """
        if not creatinina_serica or creatinina_serica <= 0:
            return None
        
        factor_sexo = 0.85 if sex in ['F', 'Femenine'] else 1.0
        numerador = (140 - age) * weight * factor_sexo
        denominador = 72 * creatinina_serica
        clearance = numerador / denominador
        
        return round(clearance, 2)
    
    @staticmethod
    def get_kidney_function_status(clearance_creatinina):
        """Clasifica la función renal según el clearance de creatinina."""
        if not clearance_creatinina:
            return "desconocido"
        
        if clearance_creatinina >= 90:
            return "normal"
        elif clearance_creatinina >= 60:
            return "leve_disminucion"
        elif clearance_creatinina >= 30:
            return "moderada_disminucion"
        elif clearance_creatinina >= 15:
            return "severa_disminucion"
        else:
            return "fallo_renal"
    
    @staticmethod
    def get_liver_function_status(alt, ast, bilirrubina_total):
        """Clasifica la función hepática según ALT, AST y bilirrubina."""
        if not (alt or ast or bilirrubina_total):
            return "desconocido"
        
        alt_elevada = alt and alt > 56
        ast_elevada = ast and ast > 40
        bilirrubina_elevada = bilirrubina_total and bilirrubina_total > 1.2
        
        elevaciones = sum([alt_elevada, ast_elevada, bilirrubina_elevada])
        
        if elevaciones == 0:
            return "normal"
        elif elevaciones == 1:
            return "leve_alteracion"
        elif elevaciones == 2:
            return "moderada_alteracion"
        else:
            alt_muy_alta = alt and alt > 150
            ast_muy_alta = ast and ast > 120
            bilirrubina_muy_alta = bilirrubina_total and bilirrubina_total > 3.0
            
            if any([alt_muy_alta, ast_muy_alta, bilirrubina_muy_alta]):
                return "severa_alteracion"
            return "moderada_alteracion"
    
    @staticmethod
    def obtener_factor_inmune(estado_inmune):
        """
        Calcula el factor inmune del paciente que afecta la supervivencia bacteriana.
        
        Un sistema inmune más débil permite mayor supervivencia bacteriana.
        
        Args:
            estado_inmune (str): Estado inmunológico del paciente
        
        Returns:
            float: Factor inmune entre 0.1 y 1.0
                   - 1.0: Normal - máxima presión inmune sobre bacterias
                   - 0.5: Inmunodeprimido - presión moderada
                   - 0.1: Inmunodeprimido severo - presión mínima
        """
        factores = {
            "normal": 1.0,
            "inmunodeprimido": 0.5,
            "inmunodeprimido_severo": 0.1
        }
        return factores.get(estado_inmune, 1.0)
    
    @staticmethod
    def get_death_rate_modifier(guest):
        """
        Calcula un modificador de la tasa de mortalidad bacteriana.
        
        Returns:
            float: Multiplicador para death_rate (1.0 = normal, <1.0 = menor efectividad)
        """
        modifier = 1.0
        
        # Ajuste por función renal
        kidney_status = GuestService.get_kidney_function_status(guest.clearance_creatinina)
        if kidney_status == "moderada_disminucion":
            modifier *= 0.85
        elif kidney_status == "severa_disminucion":
            modifier *= 0.7
        elif kidney_status == "fallo_renal":
            modifier *= 0.5
        
        # Ajuste por función hepática
        liver_status = GuestService.get_liver_function_status(
            guest.alt, guest.ast, guest.bilirrubina_total
        )
        if liver_status == "moderada_alteracion":
            modifier *= 0.9
        elif liver_status == "severa_alteracion":
            modifier *= 0.8
        
        # Ajuste por estado inmune
        if guest.estado_inmune == "inmunodeprimido":
            modifier *= 0.85
        elif guest.estado_inmune == "inmunodeprimido_severo":
            modifier *= 0.65
        
        return round(modifier, 3)
    
    @staticmethod
    def get_reproduction_rate_modifier(estado_inmune):
        """Calcula un modificador de la tasa de reproducción bacteriana."""
        if estado_inmune == "inmunodeprimido":
            return 1.3
        elif estado_inmune == "inmunodeprimido_severo":
            return 1.6
        return 1.0
    
    @staticmethod
    def get_risk_score(guest):
        """Calcula un puntaje de riesgo del paciente (0-10)."""
        score = 0
        
        if guest.age >= 65:
            score += 2
            if guest.age >= 80:
                score += 1
        
        kidney_status = GuestService.get_kidney_function_status(guest.clearance_creatinina)
        kidney_scores = {
            "normal": 0,
            "leve_disminucion": 0,
            "moderada_disminucion": 1,
            "severa_disminucion": 2,
            "fallo_renal": 3
        }
        score += kidney_scores.get(kidney_status, 0)
        
        liver_status = GuestService.get_liver_function_status(
            guest.alt, guest.ast, guest.bilirrubina_total
        )
        liver_scores = {
            "normal": 0,
            "leve_alteracion": 0,
            "moderada_alteracion": 1,
            "severa_alteracion": 2
        }
        score += liver_scores.get(liver_status, 0)
        
        if guest.estado_inmune == "inmunodeprimido":
            score += 2
        elif guest.estado_inmune == "inmunodeprimido_severo":
            score += 3
        
        return min(score, 10)
    
    @staticmethod
    def requires_dose_adjustment(guest):
        """Determina si el paciente requiere ajuste de dosis."""
        adjustments = {
            "renal": False,
            "hepatica": False,
            "inmune": False,
            "recomendaciones": []
        }
        
        kidney_status = GuestService.get_kidney_function_status(guest.clearance_creatinina)
        if kidney_status in ["moderada_disminucion", "severa_disminucion", "fallo_renal"]:
            adjustments["renal"] = True
            if kidney_status == "fallo_renal":
                adjustments["recomendaciones"].append(
                    f"⚠️ CRÍTICO: Ajuste de dosis por {kidney_status}. CrCl: {guest.clearance_creatinina} mL/min"
                )
            else:
                adjustments["recomendaciones"].append(
                    f"Ajustar dosis por función renal ({kidney_status}). CrCl: {guest.clearance_creatinina} mL/min"
                )
        
        liver_status = GuestService.get_liver_function_status(
            guest.alt, guest.ast, guest.bilirrubina_total
        )
        if liver_status in ["moderada_alteracion", "severa_alteracion"]:
            adjustments["hepatica"] = True
            adjustments["recomendaciones"].append(
                f"Ajustar dosis por función hepática ({liver_status})"
            )
        
        if guest.estado_inmune in ["inmunodeprimido", "inmunodeprimido_severo"]:
            adjustments["inmune"] = True
            adjustments["recomendaciones"].append(
                f"Paciente {guest.estado_inmune}. Considerar terapia combinada."
            )
        
        return adjustments