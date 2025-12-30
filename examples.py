"""Scénarios d'exemple pour tester le système commercial IAfluence."""

SCENARIOS = {
    "pme_shadow_ia": {
        "name": "PME - Urgence Shadow IA",
        "description": "Dirigeant de PME inquiet de l'usage non contrôlé de ChatGPT par ses équipes",
        "messages": [
            "Bonjour, je suis le DG d'une PME industrielle de 80 personnes. J'ai découvert que mes équipes utilisent ChatGPT pour tout et n'importe quoi, y compris pour des données clients. Je suis très inquiet, comment pouvez-vous m'aider ?",
            "Oui c'est urgent, on a des contrats sensibles avec des clients automobiles. Je ne sais pas ce qui a pu fuiter. Qu'est-ce que vous proposez concrètement ?",
            "Un diagnostic gratuit ça m'intéresse. Je peux avoir un créneau cette semaine ?"
        ]
    },

    "eti_strategie_ia": {
        "name": "ETI - Stratégie IA complète",
        "description": "DSI d'une ETI qui cherche à structurer une approche IA globale",
        "messages": [
            "Je suis DSI d'une ETI de 500 collaborateurs dans le secteur des services. Notre DG veut qu'on 'fasse de l'IA' mais personne ne sait vraiment par où commencer. On a besoin d'une vision structurée.",
            "On a déjà fait quelques POC avec des ESN mais ça n'a rien donné de concret. On aimerait une approche plus stratégique, pas juste technique.",
            "Quel serait le budget pour un accompagnement stratégie + gouvernance ? Et ça prendrait combien de temps ?",
            "C'est dans notre fourchette. Pouvez-vous me faire une proposition formelle que je puisse présenter au COMEX ?"
        ]
    },

    "formation_dirigeants": {
        "name": "Formation Dirigeants",
        "description": "DRH qui cherche à former le CODIR sur l'IA",
        "messages": [
            "Bonjour, je suis DRH d'une entreprise de 150 personnes. Notre CODIR est complètement perdu face à l'IA. Ils entendent parler de ChatGPT, Copilot, etc. mais ne comprennent pas les enjeux ni les risques.",
            "On aimerait une formation d'une journée pour les sensibiliser. Quelque chose de concret, pas trop technique. Ils sont 8 personnes.",
            "Vous faites aussi les équipes ? On a des managers qui auraient besoin de comprendre comment utiliser l'IA au quotidien sans prendre de risques.",
            "OK, envoyez-moi une proposition pour le CODIR + une option pour les managers."
        ]
    },

    "poc_souverain": {
        "name": "POC IA Souveraine",
        "description": "Responsable IT qui veut tester une solution IA interne",
        "messages": [
            "Bonjour, je suis responsable IT dans une entreprise du secteur santé. On ne peut pas utiliser les solutions cloud américaines pour des raisons réglementaires. Est-ce que vous pouvez nous aider à déployer un LLM en interne ?",
            "On a des serveurs dédiés, on voudrait tester un modèle open source type Mistral ou Llama. C'est faisable ?",
            "Un POC sur 2-3 cas d'usage, ça coûterait combien ? Et quel délai ?",
            "C'est raisonnable. On peut commencer quand ?"
        ]
    },

    "objection_budget": {
        "name": "Objection Budget - Négociation",
        "description": "Prospect intéressé mais avec un budget limité",
        "messages": [
            "Bonjour, j'ai une PME de 40 personnes et on aimerait former nos équipes à l'IA mais on n'a pas beaucoup de budget.",
            "3500€ pour une journée de formation c'est au-dessus de notre budget. On pensait plutôt à 1500-2000€ max.",
            "Une demi-journée ça pourrait être bien pour démarrer. Et si ça marche, on pourrait envisager la suite.",
            "D'accord pour la demi-journée découverte. On signe où ?"
        ]
    },

    "objection_timing": {
        "name": "Objection Timing - Pas maintenant",
        "description": "Prospect intéressé mais veut reporter",
        "messages": [
            "Bonjour, je suis intéressé par vos services d'accompagnement IA. On est une PME tech de 60 personnes.",
            "Votre approche me plaît, mais là on est en pleine migration de notre ERP. Ce n'est pas le bon moment pour lancer un projet IA en plus.",
            "Peut-être au Q2 2025 ? En attendant vous pouvez m'envoyer de la documentation ?",
        ]
    },

    "lead_froid": {
        "name": "Lead Froid - Curiosité",
        "description": "Prospect en simple veille, pas de projet concret",
        "messages": [
            "Bonjour, je fais de la veille sur l'IA pour mon entreprise. Qu'est-ce que vous proposez exactement ?",
            "D'accord, et ça coûte combien en général ce genre d'accompagnement ?",
            "Ah oui c'est costaud quand même. On est une petite équipe de 8, je ne suis pas sûr qu'on ait les moyens.",
            "Je vais y réfléchir. Merci pour les infos."
        ]
    },

    "escalade_grand_compte": {
        "name": "Escalade Grand Compte",
        "description": "Demande complexe d'un grand compte nécessitant l'intervention du fondateur",
        "messages": [
            "Bonjour, je représente un groupe industriel de 8000 collaborateurs. Nous cherchons un partenaire pour définir notre stratégie IA groupe avec des enjeux de souveraineté importants.",
            "Nous avons des filiales dans 5 pays européens. Il nous faut une approche qui prenne en compte les réglementations locales, le RGPD, et potentiellement l'AI Act.",
            "Nous avons un budget conséquent mais nous voulons d'abord valider que vous avez l'envergure pour ce type de projet. Pouvez-vous nous mettre en contact avec votre direction ?",
            "Parfait, je souhaite un call avec votre fondateur pour discuter des modalités."
        ]
    },

    "conversion_rapide": {
        "name": "Conversion Rapide",
        "description": "Prospect très motivé, conversion immédiate",
        "messages": [
            "Bonjour, j'ai lu votre article sur le Shadow IA sur LinkedIn. On a exactement ce problème chez nous. Je suis le CEO d'une boîte de 120 personnes.",
            "Je veux qu'on prenne les devants avant qu'il y ait un incident. Vous faites quoi comme diagnostic ?",
            "Parfait, c'est exactement ce qu'il nous faut. Comment on fait pour prendre RDV ?"
        ]
    },

    "accompagnement_global": {
        "name": "Accompagnement Global",
        "description": "Prospect qui veut un accompagnement complet sur plusieurs mois",
        "messages": [
            "Bonjour, je suis directeur de la transformation d'une ETI de 300 personnes. On veut vraiment prendre le virage de l'IA mais de façon structurée.",
            "On a besoin de tout : une stratégie claire, former nos équipes, et potentiellement déployer des outils en interne. Mais on veut y aller progressivement.",
            "Votre formule d'accompagnement global sur plusieurs mois m'intéresse. Comment ça fonctionne concrètement ?",
            "Un engagement de 3 mois pour commencer ça me va. On peut démarrer en janvier ?"
        ]
    }
}


def list_scenarios():
    """List all available scenarios."""
    print("\n📚 SCÉNARIOS DISPONIBLES - IAFLUENCE :\n")
    for key, scenario in SCENARIOS.items():
        print(f"  {key:25} - {scenario['name']}")
        print(f"  {' '*25}   {scenario['description']}\n")


if __name__ == "__main__":
    list_scenarios()
