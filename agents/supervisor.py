"""Supervisor Agent - IAfluence."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent


class SupervisorAgent(BaseAgent):
    """
    Agent superviseur IAfluence.

    Analyse l'état de la conversation et décide :
    - Si l'objectif est atteint (conversion ou qualification)
    - Quel agent doit intervenir ensuite
    - Quand escalader vers Suan Tay
    - Quand clôturer la conversation
    """

    def __init__(self, **kwargs):
        super().__init__(name="Supervisor", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor."""
        return """Tu es l'agent Superviseur d'IAfluence, qui orchestre le processus commercial.

Ton rôle est de :
1. Analyser l'état actuel de la conversation
2. Déterminer si l'objectif est atteint (rendez-vous, conversion, qualification)
3. Décider quel agent doit intervenir ensuite
4. Identifier quand une escalade vers Suan Tay est nécessaire
5. Reconnaître quand la conversation doit se terminer

CONTEXTE IAFLUENCE :
Cabinet de conseil spécialisé dans l'accompagnement IA pour PME/ETI.
Objectif principal : obtenir un rendez-vous avec Suan Tay (diagnostic gratuit).
Suan Tay intervient personnellement sur toutes les missions.

CRITÈRES DE DÉCISION :

CONVERTI (Objectif atteint) :
- Prospect accepte explicitement le diagnostic gratuit ou une offre
- Engagement clair pour un rendez-vous ou démarrage
- Demande le lien de prise de RDV
- Action : Router vers CRM_Agent

NEGOCIATION_NECESSAIRE :
- Prospect soulève des objections (prix, timing, etc.)
- Demande des modifications à la proposition
- Action : Router vers Negotiator

NOUVELLE_OFFRE_NECESSAIRE :
- Offre actuelle ne correspond pas au besoin
- Besoins du prospect ont évolué
- Demande une autre option
- Action : Router vers Seller

ESCALADE :
- Besoins très spécifiques ou complexes (ETI, grand compte)
- Trop de tours de négociation (3+)
- Prospect demande explicitement à parler au fondateur
- Projet stratégique à fort enjeu
- Action : Router vers CRM_Agent avec flag escalade

CLOTURER :
- Prospect clairement pas intéressé
- Lead non qualifié sans potentiel
- Conversation arrivée à conclusion naturelle
- Action : Router vers CRM_Agent

CONTINUER :
- Besoin de plus d'informations
- Prospect engagé mais indécis
- Questions en suspens
- Action : Attendre plus d'input

Réponds avec un JSON valide :
{{
    "analysis": "Analyse brève de la situation actuelle",
    "prospect_sentiment": "positif|neutre|negatif",
    "goal_achieved": true|false,
    "conversion_probability": 0-100,
    "next_agent": "classifier|seller|negotiator|crm|none",
    "should_escalate": true|false,
    "should_close": true|false,
    "reasoning": "Explication de ta décision",
    "recommended_action": "Ce qui devrait se passer ensuite"
}}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Supervise the sales process and route to next agent."""
        current_message = state.get("current_message", "")
        conversation_history = state.get("messages", [])
        current_agent = state.get("current_agent", "")

        # Create context summary
        context = {
            "lead_type": state.get("lead_type"),
            "lead_score": state.get("lead_score", 0),
            "qualified": state.get("qualified", False),
            "offers_made_count": len(state.get("offers_made", [])),
            "objections_count": len(state.get("objections", [])),
            "negotiation_count": state.get("negotiation_count", 0),
            "converted": state.get("converted", False),
            "escalated": state.get("escalated", False),
        }

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Analyse cette conversation commerciale et décide des prochaines étapes :

Message actuel du prospect : {message}

Contexte :
- Type de lead : {lead_type}
- Score du lead : {lead_score}
- Qualifié : {qualified}
- Offres faites : {offers_count}
- Objections : {objections_count}
- Tours de négociation : {negotiation_count}
- Converti : {converted}
- Escaladé : {escalated}
- Dernier agent : {last_agent}

Conversation récente :
{history}

Fournis ton analyse et ta décision de routage au format JSON.""")
        ])

        # Format data
        history = self.format_conversation_history(conversation_history[-5:])

        # Get analysis
        chain = prompt | self.llm
        response = chain.invoke({
            "message": current_message,
            "lead_type": context["lead_type"] or "inconnu",
            "lead_score": context["lead_score"],
            "qualified": context["qualified"],
            "offers_count": context["offers_made_count"],
            "objections_count": context["objections_count"],
            "negotiation_count": context["negotiation_count"],
            "converted": context["converted"],
            "escalated": context["escalated"],
            "last_agent": current_agent,
            "history": history or "Pas de conversation précédente"
        })

        # Parse response
        try:
            content = response.content
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)

            # Update state based on analysis
            state["sentiment"] = analysis.get("prospect_sentiment", "neutre")

            # Add insight
            state["key_insights"].append(
                f"Superviseur : {analysis.get('analysis', 'Analyse non disponible')}"
            )

            # Update agent tracking
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "supervisor"

            # Determine next action
            if analysis.get("goal_achieved") or analysis.get("should_close"):
                state["next_action"] = "crm"
                if analysis.get("should_escalate"):
                    state["escalated"] = True

            else:
                next_agent = analysis.get("next_agent", "none")
                if next_agent != "none":
                    state["next_action"] = next_agent
                else:
                    state["next_action"] = "wait_for_response"

        except json.JSONDecodeError as e:
            print(f"Error parsing supervisor response: {e}")
            print(f"Response content: {content}")
            # Default: continue conversation
            state["next_action"] = "wait_for_response"

        return state
