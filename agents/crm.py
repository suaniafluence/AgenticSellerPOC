"""CRM Agent - IAfluence."""
import json
from typing import Any, Dict
from datetime import datetime
from .base import BaseAgent


class CRMAgent(BaseAgent):
    """
    Agent CRM IAfluence.

    Enregistre les conversations, suit les opportunités,
    met à jour les informations de contact et crée des tâches de suivi.
    """

    # Coordonnées IAfluence
    CONTACT_INFO = {
        "fondateur": "Suan Tay",
        "email": "suan.tay@iafluence.fr",
        "telephone": "06 65 19 76 33",
        "calendrier": "https://calendar.app.google/BcE52KKmVRmki1kZ8",
        "site": "https://iafluence.fr"
    }

    def __init__(self, **kwargs):
        super().__init__(name="CRM_Agent", **kwargs)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data to CRM and create tasks."""
        lead_info = state.get("lead_info", {})
        session_id = state.get("session_id", "")
        converted = state.get("converted", False)
        escalated = state.get("escalated", False)

        # Create CRM record
        crm_record = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "lead_info": lead_info,
            "lead_type": state.get("lead_type"),
            "lead_score": state.get("lead_score"),
            "qualified": state.get("qualified"),
            "converted": converted,
            "escalated": escalated,
            "offers_made": state.get("offers_made", []),
            "final_offer": state.get("current_offer"),
            "objections": state.get("objections", []),
            "negotiation_rounds": state.get("negotiation_count", 0),
            "key_insights": state.get("key_insights", []),
            "sentiment": state.get("sentiment", "neutre"),
            "maturite_ia": lead_info.get("maturite_ia", "debutant"),
            "conversation_summary": self._create_summary(state),
        }

        # Simulate CRM sync (in production, this would call actual CRM API)
        print("\n" + "="*60)
        print("📊 SYNCHRONISATION CRM - IAFLUENCE")
        print("="*60)
        print(json.dumps(crm_record, indent=2, ensure_ascii=False))
        print("="*60 + "\n")

        # Create tasks for follow-up
        tasks = self._create_tasks(state)
        if tasks:
            print("📋 TÂCHES CRÉÉES :")
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task}")
            print()

        # Update state
        state["crm_synced"] = True
        state["last_agent"] = state["current_agent"]
        state["current_agent"] = "crm"

        # Add CRM sync message with IAfluence contact info
        if converted:
            message = f"""Parfait ! Je note votre intérêt pour notre accompagnement.

Pour planifier votre diagnostic gratuit avec Suan Tay, notre fondateur, vous pouvez :
- Réserver directement un créneau : {self.CONTACT_INFO['calendrier']}
- Nous contacter par email : {self.CONTACT_INFO['email']}
- Nous appeler : {self.CONTACT_INFO['telephone']}

Suan vous recontactera sous 24h pour préparer votre rendez-vous. À très bientôt !"""
        elif escalated:
            message = f"""J'ai bien noté vos besoins spécifiques.

Suan Tay, notre fondateur, va vous recontacter personnellement sous 24h pour discuter d'un accompagnement sur-mesure.

En attendant, vous pouvez :
- Réserver un créneau directement : {self.CONTACT_INFO['calendrier']}
- L'appeler : {self.CONTACT_INFO['telephone']}
- Lui écrire : {self.CONTACT_INFO['email']}

À très bientôt !"""
        else:
            message = f"""Merci pour cet échange !

Si vous souhaitez en discuter à l'avenir, n'hésitez pas à contacter Suan Tay :
- Email : {self.CONTACT_INFO['email']}
- Téléphone : {self.CONTACT_INFO['telephone']}
- Prendre RDV : {self.CONTACT_INFO['calendrier']}

IAfluence - L'IA utile, au bon endroit, au bon rythme."""

        state["messages"].append({
            "role": "assistant",
            "content": message,
            "metadata": {"agent": "crm", "synced": True}
        })

        # Mark as closed
        state["closed"] = True
        state["next_action"] = "end"

        return state

    def _create_summary(self, state: Dict[str, Any]) -> str:
        """Create a summary of the conversation."""
        messages = state.get("messages", [])
        lead_score = state.get("lead_score", 0)
        converted = state.get("converted", False)
        lead_info = state.get("lead_info", {})

        message_count = len(messages)

        if converted:
            status = "✅ CONVERTI"
        elif state.get("escalated"):
            status = "⬆️ ESCALADE"
        elif state.get("qualified"):
            status = "🔥 QUALIFIÉ"
        else:
            status = "❄️ NON QUALIFIÉ"

        maturite = lead_info.get("maturite_ia", "inconnu")
        offre_reco = lead_info.get("offre_recommandee", "DIAGNOSTIC")

        return f"{status} | Score: {lead_score} | Maturité IA: {maturite} | Offre reco: {offre_reco} | Messages: {message_count}"

    def _create_tasks(self, state: Dict[str, Any]) -> list:
        """Create tasks for follow-up."""
        tasks = []
        lead_info = state.get("lead_info", {})

        if state.get("converted"):
            tasks.append("📅 Envoyer confirmation de RDV diagnostic")
            tasks.append("📧 Envoyer email de préparation au diagnostic")
            tasks.append(f"📞 Appeler pour confirmer le créneau - {self.CONTACT_INFO['telephone']}")
            if lead_info.get("offre_recommandee"):
                tasks.append(f"📝 Préparer proposition {lead_info.get('offre_recommandee')}")

        elif state.get("escalated"):
            tasks.append("🔔 Suan Tay doit rappeler sous 24h")
            tasks.append("📄 Préparer proposition sur-mesure")
            objections = state.get("objections", [])
            if objections:
                tasks.append(f"🎯 Adresser les objections : {', '.join(objections[:3])}")
            if lead_info.get("company_size") in ["eti", "grand_compte"]:
                tasks.append("💼 Préparer offre ETI/Grand compte personnalisée")

        elif state.get("qualified"):
            tasks.append("📧 Envoyer email de suivi dans 3-5 jours")
            tasks.append("📚 Envoyer documentation adaptée au secteur")
            if lead_info.get("pain_points"):
                tasks.append(f"🎯 Contenu ciblé sur : {', '.join(lead_info.get('pain_points', [])[:2])}")

        else:
            tasks.append("📧 Ajouter à la newsletter IAfluence")
            tasks.append("🔄 Relancer dans 30 jours")
            tasks.append("📱 Connecter sur LinkedIn")

        return tasks
