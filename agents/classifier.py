"""Prospect Classifier Agent - IAfluence."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent
from state import LeadType, LeadSector, CompanySize


class ProspectClassifier(BaseAgent):
    """
    Agent de qualification des prospects IAfluence.

    Analyse les messages des prospects pour déterminer :
    - Type de lead (chaud/tiède/froid)
    - Secteur d'activité
    - Taille d'entreprise (PME/ETI)
    - Maturité IA et problématiques
    - Niveau décisionnel
    """

    def __init__(self, **kwargs):
        super().__init__(name="Prospect_Classifier", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the classifier."""
        return """Tu es l'agent de qualification des prospects d'IAfluence, cabinet spécialisé dans l'accompagnement IA pour PME et ETI.

Ton rôle est de :
1. Classifier les leads comme CHAUD, TIEDE ou FROID selon leur message
2. Identifier le secteur d'activité
3. Estimer la taille de l'entreprise (STARTUP, PME, ETI, GRAND_COMPTE)
4. Évaluer la maturité IA et détecter les problématiques
5. Déterminer si c'est un décideur (dirigeant, DG, DSI, DRH, directeur)
6. Calculer un score de lead (0-100)

CONTEXTE IAFLUENCE :
IAfluence accompagne les PME/ETI dans la structuration et sécurisation des usages IA.
Cibles prioritaires : PME de 20-250 salariés, ETI de 250-5000 salariés.
Problématiques types : Shadow IA, gouvernance IA, formation équipes, souveraineté données.

CRITÈRES DE CLASSIFICATION :

CHAUD (Score 70-100) :
- Besoin immédiat et urgent d'accompagnement IA
- Budget identifié ou décideur avec pouvoir d'engagement
- Problématique concrète : Shadow IA, formation urgente, projet IA en cours
- Demande explicite de rendez-vous ou devis

TIEDE (Score 40-69) :
- Intéressé mais pas d'urgence immédiate
- En phase d'exploration ou de veille
- Besoin d'approbation hiérarchique
- Questions générales sur l'IA en entreprise

FROID (Score 0-39) :
- Curiosité générale sans projet concret
- Budget non défini ou très limité
- Entreprise trop petite (< 10 personnes) ou trop grande (> 5000)
- Pas de problématique IA identifiée

SECTEURS :
- industrie : Manufacturing, production, industrie lourde
- services : Conseil, services aux entreprises, ESN
- commerce : Retail, e-commerce, distribution
- finance : Banque, assurance, fintech
- sante : Santé, pharma, medtech
- tech : Éditeur logiciel, SaaS, startup tech
- immobilier : Promotion, gestion immobilière
- autre : Autres secteurs

TAILLE ENTREPRISE :
- startup : 1-19 salariés (hors cible prioritaire)
- pme : 20-249 salariés (cible idéale)
- eti : 250-4999 salariés (cible idéale)
- grand_compte : 5000+ salariés (potentiel mais complexe)

PROBLÉMATIQUES IA TYPIQUES :
- Shadow IA : usage non contrôlé de ChatGPT, Copilot, etc.
- Gouvernance : absence de charte, règles floues
- Formation : équipes non formées, peur de l'IA
- Sécurité données : risques de fuite d'informations sensibles
- Souveraineté : dépendance aux GAFAM, besoin de solutions internes
- ROI : difficulté à mesurer la valeur de l'IA
- Intégration : besoin de POC ou déploiement technique

Réponds UNIQUEMENT avec un JSON valide dans ce format exact :
{
    "lead_type": "chaud|tiede|froid",
    "sector": "industrie|services|commerce|finance|sante|tech|immobilier|autre",
    "company_size": "startup|pme|eti|grand_compte",
    "decision_maker": true|false,
    "maturite_ia": "debutant|explorateur|avance",
    "pain_points": ["problématique1", "problématique2"],
    "interests": ["intérêt1", "intérêt2"],
    "lead_score": 0-100,
    "reasoning": "Explication brève de la classification",
    "key_insights": ["insight1", "insight2"],
    "offre_recommandee": "DIAGNOSTIC|STRATEGIE|FORMATION|EXPERTISE|ACCOMPAGNEMENT_GLOBAL"
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the prospect based on their message."""
        current_message = state.get("current_message", "")
        conversation_history = state.get("messages", [])

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Analyse ce prospect :

Message récent : {message}

Historique de conversation :
{history}

Fournis ta classification au format JSON.""")
        ])

        # Format history
        history = self.format_conversation_history(conversation_history[-5:])

        # Get classification
        chain = prompt | self.llm
        response = chain.invoke({
            "message": current_message,
            "history": history or "Pas de conversation précédente"
        })

        # Parse response
        try:
            # Extract JSON from response
            content = response.content
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            classification = json.loads(content)

            # Update state
            lead_info = state.get("lead_info", {})
            lead_info["sector"] = classification.get("sector")
            lead_info["company_size"] = classification.get("company_size")
            lead_info["decision_maker"] = classification.get("decision_maker", False)
            lead_info["pain_points"] = classification.get("pain_points", [])
            lead_info["interests"] = classification.get("interests", [])
            lead_info["maturite_ia"] = classification.get("maturite_ia", "debutant")
            lead_info["offre_recommandee"] = classification.get("offre_recommandee", "DIAGNOSTIC")

            state["lead_info"] = lead_info
            state["lead_type"] = classification.get("lead_type")
            state["lead_score"] = classification.get("lead_score", 0)
            state["qualified"] = classification.get("lead_score", 0) >= 40  # Seuil abaissé pour IAfluence

            # Add insights
            insights = classification.get("key_insights", [])
            state["key_insights"].extend(insights)

            # Update current agent
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "classifier"

            # Determine next action based on qualification
            if state["qualified"]:
                state["next_action"] = "seller"
                state["context"] = "qualified_lead"
            else:
                state["next_action"] = "nurture"
                state["context"] = "unqualified_lead"

        except json.JSONDecodeError as e:
            print(f"Error parsing classifier response: {e}")
            print(f"Response content: {content}")
            # Set defaults if parsing fails
            state["qualified"] = False
            state["lead_score"] = 0
            state["next_action"] = "seller"  # Try seller anyway

        return state
