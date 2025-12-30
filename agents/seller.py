"""Seller Agent - IAfluence."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent


class SellerAgent(BaseAgent):
    """
    Agent commercial IAfluence spécialisé dans l'accompagnement IA pour PME/ETI.

    Analyse les besoins du prospect et propose des offres personnalisées
    autour des 3 piliers IAfluence : Stratégie, Formation, Expertise technique.
    """

    def __init__(self, **kwargs):
        super().__init__(name="Seller", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the seller."""
        return """Tu es l'assistant commercial IA d'IAfluence, cabinet de conseil spécialisé dans l'accompagnement IA pour PME et ETI.

Ton rôle est de :
1. Analyser les besoins, problématiques et budget du prospect
2. Créer une offre personnalisée adaptée à leur maturité IA
3. Mettre en avant les bénéfices pertinents
4. Proposer des modalités d'engagement (diagnostic, accompagnement, formation)
5. Présenter l'offre de manière claire et rassurante

POSITIONNEMENT IAFLUENCE :
IAfluence accompagne les PME et ETI dans la structuration, la sécurisation et l'industrialisation de leurs usages IA.
Approche pragmatique, souveraine et orientée valeur métier.
L'IA utile, au bon endroit, au bon rythme.

OFFRES DISPONIBLES :

1. DIAGNOSTIC IA (Gratuit ou 490€)
   - Échange de 45 min avec Suan Tay, fondateur
   - Audit des usages IA actuels (officiels et Shadow IA)
   - Évaluation de la maturité IA
   - Recommandations personnalisées
   - Idéal pour : première prise de contact

2. STRATEGIE IA & GOUVERNANCE (à partir de 3 500€)
   - Définition d'une stratégie IA alignée avec les enjeux métiers
   - Rédaction d'une charte IA (usages autorisés/interdits, sécurité)
   - Cartographie et lutte contre le Shadow IA
   - Trajectoire vers la souveraineté IA si nécessaire
   - Durée : 2-4 semaines selon périmètre

3. FORMATION & MONTÉE EN COMPÉTENCES (à partir de 1 500€/jour)
   - Dirigeants & managers : compréhension stratégique, risques, opportunités
   - Équipes métiers : usages avancés, productivité, automatisation
   - Équipes IT : LLM, intégration et exploitation de solutions IA internes
   - Formats : présentiel, distanciel, sur mesure

4. EXPERTISE TECHNIQUE & POC (à partir de 5 000€)
   - Conception d'infrastructures IA internes et souveraines
   - Déploiement de modèles de langage sur serveurs dédiés
   - Réalisation de POC ciblés pour valider la valeur métier
   - Accompagnement sur mesure selon la maturité IA
   - Durée : selon complexité

5. ACCOMPAGNEMENT GLOBAL (forfait mensuel à partir de 2 500€/mois)
   - Combinaison des 3 piliers selon les besoins
   - Suivi régulier et montée en compétences progressive
   - Engagement minimum 3 mois
   - Idéal pour : transformation IA complète

INCITATIONS POSSIBLES :
- Diagnostic gratuit pour première prise de contact
- Remise de 10-15% pour engagement trimestriel/annuel
- Offre découverte formation 1/2 journée
- POC pilote à tarif réduit pour tester l'approche

Réponds avec un JSON valide dans ce format :
{
    "offre": "DIAGNOSTIC|STRATEGIE|FORMATION|EXPERTISE|ACCOMPAGNEMENT_GLOBAL",
    "tarif": montant_en_euros,
    "duree": "durée estimée",
    "contenu": ["élément1", "élément2"],
    "remise": 0-15,
    "prochaine_etape": "diagnostic gratuit|appel découverte|proposition détaillée",
    "engagement": "ponctuel|trimestriel|annuel",
    "conditions": ["condition1"],
    "pitch": "Texte de proposition commerciale personnalisée",
    "reasoning": "Pourquoi cette offre correspond à leurs besoins"
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized sales offer."""
        lead_info = state.get("lead_info", {})
        current_message = state.get("current_message", "")
        conversation_history = state.get("messages", [])
        objections = state.get("objections", [])

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Crée une proposition commerciale pour ce prospect :

Informations sur le lead :
- Secteur : {sector}
- Taille entreprise : {company_size}
- Décideur : {decision_maker}
- Problématiques : {pain_points}
- Intérêts : {interests}
- Score du lead : {lead_score}

Message récent : {message}

Objections précédentes : {objections}

Historique de conversation :
{history}

Crée une proposition personnalisée et convaincante au format JSON.""")
        ])

        # Format data
        history = self.format_conversation_history(conversation_history[-5:])

        # Get offer
        chain = prompt | self.llm
        response = chain.invoke({
            "sector": lead_info.get("sector", "inconnu"),
            "company_size": lead_info.get("company_size", "inconnu"),
            "decision_maker": lead_info.get("decision_maker", False),
            "pain_points": ", ".join(lead_info.get("pain_points", [])),
            "interests": ", ".join(lead_info.get("interests", [])),
            "lead_score": state.get("lead_score", 0),
            "message": current_message,
            "objections": ", ".join(objections) if objections else "Aucune",
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

            offer_data = json.loads(content)

            # Create offer
            offer = {
                "offre": offer_data.get("offre"),
                "tarif": offer_data.get("tarif"),
                "duree": offer_data.get("duree"),
                "contenu": offer_data.get("contenu", []),
                "remise": offer_data.get("remise", 0),
                "prochaine_etape": offer_data.get("prochaine_etape"),
                "engagement": offer_data.get("engagement"),
                "conditions": offer_data.get("conditions", []),
            }

            # Update state
            state["current_offer"] = offer
            state["offers_made"].append(offer)

            # Add the sales pitch as a message
            pitch = offer_data.get("pitch", "")
            state["messages"].append({
                "role": "assistant",
                "content": pitch,
                "metadata": {"agent": "seller", "offer": offer}
            })

            # Update agent tracking
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "seller"
            state["context"] = "offer_presented"

            # Next action depends on prospect response
            state["next_action"] = "wait_for_response"

        except json.JSONDecodeError as e:
            print(f"Error parsing seller response: {e}")
            print(f"Response content: {content}")
            # Fallback: add raw response as message
            state["messages"].append({
                "role": "assistant",
                "content": response.content,
                "metadata": {"agent": "seller", "error": "parse_failed"}
            })

        return state
