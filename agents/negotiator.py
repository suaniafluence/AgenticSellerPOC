"""Negotiator Agent - IAfluence."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent


class NegotiatorAgent(BaseAgent):
    """
    Agent de négociation IAfluence.

    Gère les objections, ajuste les propositions et trouve des solutions
    mutuellement satisfaisantes pour conclure l'accompagnement.
    """

    def __init__(self, **kwargs):
        super().__init__(name="Negotiator", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the negotiator."""
        return """Tu es l'agent de négociation d'IAfluence, spécialisé dans la gestion des objections pour les missions de conseil IA.

Ton rôle est de :
1. Identifier et catégoriser les objections (budget, timing, décision, confiance, etc.)
2. Répondre avec empathie et des arguments concrets
3. Ajuster les propositions dans les limites autorisées
4. Trouver des solutions créatives qui satisfont les deux parties
5. Savoir quand proposer un appel avec Suan Tay, le fondateur

POSITIONNEMENT IAFLUENCE :
IAfluence = L'IA utile, au bon endroit, au bon rythme.
Approche pragmatique, souveraine et orientée valeur métier.
Suan Tay intervient personnellement sur chaque mission.

RÈGLES DE NÉGOCIATION :

1. FLEXIBILITÉ TARIFAIRE :
   - Remise max : 15% (pour engagement trimestriel ou annuel)
   - Possibilité de paiement échelonné (3-4 mensualités)
   - Diagnostic gratuit toujours proposable comme première étape
   - POC pilote à tarif réduit (-20%) pour tester l'approche

2. FLEXIBILITÉ CONTENU :
   - Ajustement du périmètre plutôt que du prix
   - Possibilité de démarrer petit et étendre ensuite
   - Formation demi-journée découverte (500€)
   - Accompagnement progressif sur plusieurs phases

3. ESCALADE :
   - Après 3 tours de négociation : proposer appel avec Suan Tay
   - Demande client explicite de parler au fondateur
   - Besoins très spécifiques ou complexes

CATÉGORIES D'OBJECTIONS :

- BUDGET : "Trop cher", "Budget serré", "Pas les moyens"
  → Proposer échelonnement, phase pilote, diagnostic gratuit, réduction périmètre

- TIMING : "Pas maintenant", "L'année prochaine", "Pas prioritaire"
  → Créer urgence (risques Shadow IA), proposer démarrage léger, diagnostic préparatoire

- AUTORITE : "Dois en parler à...", "Pas seul décideur", "Validation nécessaire"
  → Proposer présentation pour le comité, documentation, call avec décideurs

- CONFIANCE : "Pas sûr du ROI", "Besoin de références", "C'est nouveau pour nous"
  → Témoignages clients, étude de cas, garantie satisfaction, démarrage progressif

- CONCURRENCE : "On travaille déjà avec...", "J'ai une autre proposition"
  → Différenciation IAfluence (approche souveraine, sur-mesure, fondateur impliqué)

- TECHNIQUE : "Nos équipes ne sont pas prêtes", "Infrastructure pas adaptée"
  → Formation préalable, accompagnement progressif, évaluation maturité

Réponds avec un JSON valide :
{{
    "objection_category": "BUDGET|TIMING|AUTORITE|CONFIANCE|CONCURRENCE|TECHNIQUE",
    "objection_summary": "Résumé bref de l'objection",
    "response_strategy": "Comment tu vas l'adresser",
    "adjusted_offer": {{
        "offre": "type d'offre ajustée",
        "tarif": tarif_ajusté,
        "remise": 0-15,
        "duree": "durée ajustée",
        "engagement": "ponctuel|trimestriel|annuel",
        "conditions": ["nouvelles conditions"],
        "contenu": ["éléments inclus"]
    }},
    "response": "Ta réponse au prospect (conversationnelle et empathique)",
    "should_escalate": true|false,
    "escalation_reason": "Raison de l'escalade (si applicable)"
}}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle objections and negotiate."""
        current_message = state.get("current_message", "")
        current_offer = state.get("current_offer", {})
        objections = state.get("objections", [])
        negotiation_count = state.get("negotiation_count", 0)
        lead_info = state.get("lead_info", {})
        conversation_history = state.get("messages", [])

        # Check if we've negotiated too many times
        if negotiation_count >= 3:
            state["escalated"] = True
            state["next_action"] = "escalate"
            state["messages"].append({
                "role": "assistant",
                "content": "Je comprends vos préoccupations et je souhaite vraiment trouver une solution adaptée à vos besoins. Je vous propose d'organiser un échange direct avec Suan Tay, notre fondateur, qui pourra vous proposer un accompagnement totalement sur-mesure. Seriez-vous disponible pour un appel de 30 minutes cette semaine ?",
                "metadata": {"agent": "negotiator", "action": "escalate"}
            })
            return state

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Gère cette négociation :

Message du prospect : {message}

Offre actuelle :
- Type : {offre}
- Tarif : {tarif}€
- Remise : {remise}%
- Durée : {duree}
- Contenu : {contenu}

Objections précédentes : {previous_objections}
Tour de négociation : {negotiation_round}

Contexte du lead :
- Secteur : {sector}
- Taille entreprise : {company_size}
- Score du lead : {lead_score}
- Maturité IA : {maturite_ia}

Historique de conversation :
{history}

Fournis ta réponse de négociation au format JSON.""")
        ])

        # Format data
        history = self.format_conversation_history(conversation_history[-5:])

        # Get negotiation response
        chain = prompt | self.llm
        response = chain.invoke({
            "message": current_message,
            "offre": current_offer.get("offre", "N/A"),
            "tarif": current_offer.get("tarif", 0),
            "remise": current_offer.get("remise", 0),
            "duree": current_offer.get("duree", "N/A"),
            "contenu": ", ".join(current_offer.get("contenu", [])),
            "previous_objections": ", ".join(objections[-3:]) if objections else "Aucune",
            "negotiation_round": negotiation_count + 1,
            "sector": lead_info.get("sector", "inconnu"),
            "company_size": lead_info.get("company_size", "inconnu"),
            "lead_score": state.get("lead_score", 0),
            "maturite_ia": lead_info.get("maturite_ia", "debutant"),
            "history": history or "Pas de conversation précédente"
        })

        # Parse response
        try:
            negotiation = self.parse_llm_json(response.content)

            # Track objection
            objection_summary = negotiation.get("objection_summary", current_message)
            state["objections"].append(objection_summary)

            # Update offer if adjusted
            if "adjusted_offer" in negotiation:
                adjusted_offer = negotiation["adjusted_offer"]
                state["current_offer"] = adjusted_offer
                state["offers_made"].append(adjusted_offer)

            # Add response to conversation
            response_text = negotiation.get("response", "")
            state["messages"].append({
                "role": "assistant",
                "content": response_text,
                "metadata": {
                    "agent": "negotiator",
                    "objection_category": negotiation.get("objection_category"),
                    "negotiation_round": negotiation_count + 1
                }
            })

            # Update state
            state["negotiation_count"] = negotiation_count + 1
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "negotiator"
            state["context"] = "negotiating"

            # Check for escalation
            if negotiation.get("should_escalate", False):
                state["escalated"] = True
                state["next_action"] = "escalate"
                state["key_insights"].append(
                    f"Escalade nécessaire : {negotiation.get('escalation_reason', 'Raison non précisée')}"
                )
            else:
                state["next_action"] = "wait_for_response"

        except json.JSONDecodeError as e:
            print(f"Error parsing negotiator response: {e}")
            print(f"Response content: {content}")
            # Fallback: add raw response
            state["messages"].append({
                "role": "assistant",
                "content": response.content,
                "metadata": {"agent": "negotiator", "error": "parse_failed"}
            })

        return state
