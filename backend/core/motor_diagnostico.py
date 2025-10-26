from .base_conocimientos import BaseConocimientos
from typing import List, Dict, Any, Optional
from collections import Counter
import random

class MotorDiagnostico:
    """
    Motor de inferencia multimaquinaria con lógica Akinator/procedural.
    Utiliza la clase BaseConocimientos para la fuente de datos.
    """
    def __init__(self, bk: BaseConocimientos):
        self.bk = bk
        print("✅ Motor de diagnóstico (Multimáquina) listo.")

    def _get_entries_by_prop(self, prop_prefix: str) -> Dict[str, Entry]:
        """Filtra las entradas por un prefijo de propiedad (ej. 'MAQUINA:')."""
        result = {}
        for entry in self.bk.entries:
            for prop in entry.properties:
                if prop.startswith(prop_prefix):
                    key = prop.split(': ')[1]
                    result[key] = entry
                    break
        return result

    def listar_maquinaria(self) -> Dict[str, str]:
        """Devuelve un diccionario de las máquinas disponibles (ID: Nombre)."""
        maquinas = {}
        # Asume que el nombre de la máquina está en una propiedad 'MAQUINA: Nombre'
        for entry in self.bk.entries:
            for prop in entry.properties:
                if prop.startswith("MAQUINA:"):
                    maquina_id = prop.split(': ')[1].lower().replace(" ", "_")
                    maquinas[maquina_id] = prop.split(': ')[1]
                    break
        return maquinas

    def _get_entry_index(self, name: str) -> Optional[int]:
        """Busca el índice de una entrada por nombre."""
        for i, entry in enumerate(self.bk.entries):
            if entry.name == name:
                return i
        return None

    def _get_falla_por_atributos(self, posibles_indices: List[int], atributos_actuales: List[str]) -> Optional[int]:
        """Intenta identificar la falla única si los atributos coinciden."""
        
        fallas_coincidentes = []

        for index in posibles_indices:
            entry = self.bk.entries[index]
            
            # Verifica si la entrada contiene todos los atributos proporcionados
            # Esto es una simplificación del Akinator, pero funciona para un diagnóstico preciso.
            es_coincidente = True
            for attr in atributos_actuales:
                if attr not in entry.properties:
                    es_coincidente = False
                    break
            
            if es_coincidente:
                fallas_coincidentes.append(index)

        return fallas_coincidentes[0] if len(fallas_coincidentes) == 1 else None

    def _calcular_siguiente_paso(self, posibles_indices: List[int], atributos_preguntados: List[str], id_maquina: str) -> Dict[str, Any]:
        """Decide la siguiente pregunta o pasa a la solución."""
        
        if not posibles_indices:
             return {"tipo": "final", "mensaje": "No se encontró ninguna falla que coincida con tus síntomas. Sugerimos contactar a un especialista."}

        if len(posibles_indices) == 1:
            # Falla única encontrada. Pasa al modo 'solucion'.
            falla_obj = self.bk.entries[posibles_indices[0]]
            paso_inicial = next((p for p in falla_obj.properties if p.startswith("SOLUCION_PASO_1:")), 
                                "SOLUCION_PASO_1: Se requiere soporte técnico.")
            
            return {
                "tipo": "instruccion",
                "texto": f"Diagnóstico: {falla_obj.description}. Primer Paso: {paso_inicial.split(': ')[1]}",
                "falla_activa_name": falla_obj.name,
                "paso_solucion_actual": 1
            }

        # Si hay más de una falla, elegimos la mejor pregunta (simplificado)
        candidatos_a_pregunta = [p for p in self.bk.get_all_props() if p.startswith("PREGUNTA:") and p not in atributos_preguntados]
        
        if not candidatos_a_pregunta:
            # No hay más preguntas para desempatar, se listan las fallas posibles
            nombres_fallas = [self.bk.entries[i].name for i in posibles_indices]
            return {"tipo": "final", "mensaje": f"No se pudo determinar la falla exacta. Posibilidades restantes: {', '.join(nombres_fallas)}. Contacte a soporte."}

        # Elegimos una pregunta al azar (o puedes usar lógica Counter para optimizar)
        mejor_pregunta = random.choice(candidatos_a_pregunta)

        return {
            "tipo": "pregunta", 
            "atributo_actual": mejor_pregunta, 
            "pregunta": mejor_pregunta.split(': ')[1]
        }

    def iniciar_diagnostico(self, id_maquina: str, descripcion: str) -> Dict[str, Any]:
        """Inicia una nueva sesión de diagnóstico."""
        
        # Aquí se implementaría la lógica para extraer atributos iniciales del texto libre.
        # Por simplicidad, asumimos que todos los síntomas son iniciales y nos quedamos con todas las fallas de esa máquina.
        posibles_fallas_indices = [i for i, entry in enumerate(self.bk.entries) if f"MAQUINA: {id_maquina.replace('_', ' ')}" in entry.properties]
        atributos_preguntados = [] # Inicialmente vacío

        siguiente_paso = self._calcular_siguiente_paso(posibles_fallas_indices, atributos_preguntados, id_maquina)
        
        if siguiente_paso.get('tipo') == 'pregunta':
            estado_base = {
                "modo": "diagnostico",
                "id_maquina": id_maquina,
                "posibles_fallas_indices": posibles_fallas_indices,
                "atributos_preguntados": [siguiente_paso['atributo_actual']]
            }
        else:
            # Si es instruccion/final, el estado se resuelve internamente
            estado_base = {
                 "modo": siguiente_paso.get('modo', 'solucion'),
                 "id_maquina": id_maquina
            }

        # El frontend necesita el estado para continuar
        siguiente_paso['estado'] = estado_base 
        return siguiente_paso

    def procesar_respuesta(self, estado: Dict[str, Any], respuesta_usuario: str) -> Dict[str, Any]:
        """Procesa la respuesta del usuario y avanza en el flujo."""
        
        id_maquina = estado.get("id_maquina")
        modo = estado.get("modo", "diagnostico")

        if modo == "diagnostico":
            posibles_indices = estado.get('posibles_fallas_indices', [])
            atributos_preguntados = estado.get('atributos_preguntados', [])
            atributo_actual = atributos_preguntados[-1]

            # 1. Filtrar fallas basadas en la respuesta del usuario
            fallas_filtradas = []
            for index in posibles_indices:
                entry = self.bk.entries[index]
                if respuesta_usuario.lower() == 'si':
                    if atributo_actual in entry.properties:
                        fallas_filtradas.append(index)
                else: # 'no'
                    if atributo_actual not in entry.properties:
                        fallas_filtradas.append(index)

            # 2. Calcular siguiente paso (pregunta o solución)
            siguiente_paso = self._calcular_siguiente_paso(fallas_filtradas, atributos_preguntados, id_maquina)
            
            # 3. Construir el nuevo estado para el frontend
            nuevo_estado = estado.copy()
            nuevo_estado['posibles_fallas_indices'] = fallas_filtradas
            
            if siguiente_paso.get('tipo') == 'pregunta':
                nuevo_estado['atributos_preguntados'].append(siguiente_paso['atributo_actual'])
            
            siguiente_paso['estado'] = nuevo_estado
            return siguiente_paso

        elif modo == "solucion":
            falla_name = estado.get('falla_activa_name')
            paso_actual_index = estado.get('paso_solucion_actual', 1)
            
            falla_entry = next((e for e in self.bk.entries if e.name == falla_name), None)

            if respuesta_usuario.lower() == 'si':
                return {"tipo": "final", "mensaje": f"¡Éxito! El problema '{falla_entry.description}' ha sido solucionado. ¡Excelente trabajo!"}

            # Si la respuesta es 'no', avanzamos al siguiente paso (SOLUCION_PASO_X)
            siguiente_paso_index = paso_actual_index + 1
            prop_key = f"SOLUCION_PASO_{siguiente_paso_index}:"
            
            # Buscar el siguiente paso en las propiedades
            siguiente_paso_prop = next((p for p in falla_entry.properties if p.startswith(prop_key)), None)

            if siguiente_paso_prop:
                nuevo_estado = estado.copy()
                nuevo_estado['paso_solucion_actual'] = siguiente_paso_index
                
                return {
                    "tipo": "instruccion",
                    "texto": siguiente_paso_prop.split(': ')[1],
                    "estado": nuevo_estado
                }
            else:
                return {"tipo": "final", "mensaje": f"Hemos agotado todos los pasos de solución para '{falla_name}'. Contacte a un especialista de Big Tools."}
