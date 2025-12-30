# 🚀 IAfluence - Assistant Commercial IA Multi-Agents

Système de vente autonome multi-agents propulsé par **LangGraph** pour accompagner les PME et ETI dans leur transformation IA.

## 🎯 À propos d'IAfluence

**IAfluence** accompagne les PME et ETI dans la structuration, la sécurisation et l'industrialisation de leurs usages de l'intelligence artificielle.

> *L'IA utile, au bon endroit, au bon rythme.*

### Les 3 Piliers IAfluence

| Pilier | Description |
|--------|-------------|
| **Stratégie IA & Gouvernance** | Charte IA, lutte contre le Shadow IA, trajectoire vers la souveraineté |
| **Formation & Montée en compétences** | Dirigeants, équipes métiers, équipes IT |
| **Expertise technique & POC** | Infrastructure IA souveraine, déploiement LLM, POC ciblés |

## 🏗️ Architecture Multi-Agents

Le système utilise 5 agents spécialisés orchestrés par LangGraph :

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Decision Node                     │
│              (Multi-Agent Control Plane)                 │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Classifier  │ │    Seller    │ │  Negotiator  │
│              │ │              │ │              │
│ - Qualifier  │ │ - Proposer   │ │ - Gérer      │
│ - Scorer     │ │   offres     │ │   objections │
│ - Analyser   │ │ - Pitcher    │ │ - Ajuster    │
└──────────────┘ └──────────────┘ └──────────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
        ┌────────────────────────┐
        │      Supervisor        │
        │ - Analyser état        │
        │ - Router décisions     │
        │ - Détecter conversion  │
        └────────────┬───────────┘
                     ▼
        ┌────────────────────────┐
        │       CRM Agent        │
        │ - Synchroniser data    │
        │ - Créer tâches suivi   │
        │ - Générer insights     │
        └────────────────────────┘
```

### Description des Agents

| Agent | Rôle | Capacités |
|-------|------|-----------|
| **Classifier** | Qualification | Détecte type de lead (chaud/tiède/froid), secteur, taille, maturité IA, problématiques. Score 0-100. |
| **Seller** | Création d'offres | Propose des offres personnalisées selon les besoins : Diagnostic, Stratégie, Formation, Expertise, Accompagnement global. |
| **Negotiator** | Gestion objections | Identifie les objections (budget, timing, autorité, confiance), ajuste les propositions, trouve des solutions. |
| **Supervisor** | Orchestration | Analyse l'état de la conversation, route vers les bons agents, détecte la conversion, déclenche l'escalade. |
| **CRM Agent** | Gestion données | Synchronise avec le CRM, crée les tâches de suivi, fournit les coordonnées de Suan Tay. |

## 🚀 Démarrage Rapide

### Installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd AgenticSellerPOC
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement**
```bash
cp .env.example .env
# Éditer .env et ajouter vos clés API
```

Clés API requises :
- `OPENAI_API_KEY` - Pour GPT-4 (recommandé)
- `ANTHROPIC_API_KEY` - Pour Claude (alternative)

### Utilisation

#### Démo Interactive

Lancez une conversation interactive en tant que prospect :

```bash
python main.py demo
```

#### Scénarios Prédéfinis

Exécutez un des scénarios d'exemple :

```bash
python main.py scenario pme_shadow_ia
python main.py scenario eti_strategie_ia
python main.py scenario formation_dirigeants
```

Scénarios disponibles :
- `pme_shadow_ia` - PME urgence Shadow IA
- `eti_strategie_ia` - ETI stratégie complète
- `formation_dirigeants` - Formation CODIR
- `poc_souverain` - POC IA souveraine secteur santé
- `objection_budget` - Négociation budget limité
- `objection_timing` - Report de projet
- `lead_froid` - Lead en veille simple
- `escalade_grand_compte` - Grand compte nécessitant le fondateur
- `conversion_rapide` - Conversion immédiate
- `accompagnement_global` - Package complet sur plusieurs mois

Lister tous les scénarios :
```bash
python main.py list
```

## 📊 Exemple de Conversation

```
👤 PROSPECT : Bonjour, je suis le DG d'une PME de 80 personnes.
             Mes équipes utilisent ChatGPT sans contrôle, je suis inquiet.

🔍 CLASSIFIER : [Analyse → Lead CHAUD, Industrie, PME, Score: 85/100]
               Problématique : Shadow IA, sécurité données

💼 SELLER : Je comprends votre inquiétude, c'est un sujet critique.
           IAfluence peut vous aider avec :
           - Un diagnostic gratuit de 45 min avec Suan Tay
           - Une cartographie des usages IA non contrôlés
           - Des recommandations personnalisées

           Souhaitez-vous réserver un créneau ?

👤 PROSPECT : Oui, c'est urgent. Je peux avoir un RDV cette semaine ?

👨‍💼 SUPERVISOR : [Détecte → CONVERSION]

📊 CRM : Parfait ! Voici comment réserver :
        - Calendrier : https://calendar.app.google/BcE52KKmVRmki1kZ8
        - Email : suan.tay@iafluence.fr
        - Téléphone : 06 65 19 76 33

        Suan vous recontactera sous 24h !

✅ RÉSULTAT : Converti | Score: 85/100 | 4 messages
```

## 💼 Offres IAfluence

| Offre | Tarif | Description |
|-------|-------|-------------|
| **DIAGNOSTIC IA** | Gratuit / 490€ | Échange de 45 min, audit usages IA, recommandations |
| **STRATÉGIE IA** | À partir de 3 500€ | Stratégie, charte IA, lutte Shadow IA (2-4 semaines) |
| **FORMATION** | À partir de 1 500€/jour | Dirigeants, métiers, IT - présentiel ou distanciel |
| **EXPERTISE TECHNIQUE** | À partir de 5 000€ | POC, infrastructure souveraine, déploiement LLM |
| **ACCOMPAGNEMENT GLOBAL** | À partir de 2 500€/mois | Combinaison des 3 piliers, engagement 3 mois min |

## 🔧 Configuration

### Règles de Négociation

Configurables dans `agents/negotiator.py` :
- Remise maximum : 15% (engagement trimestriel/annuel)
- Paiement échelonné : 3-4 mensualités possibles
- Escalade automatique : après 3 tours de négociation
- Diagnostic gratuit : toujours proposable

### Critères de Qualification

Configurables dans `agents/classifier.py` :
- **Lead Chaud** (70-100) : Besoin urgent, décideur, budget identifié
- **Lead Tiède** (40-69) : Intéressé, exploration, pas d'urgence
- **Lead Froid** (0-39) : Curiosité, pas de projet, budget limité

## 💾 Persistance

Le système supporte deux modes de stockage :

### Mémoire (Défaut)
Rapide, pour tests et démos. Données perdues au redémarrage.

### Fichiers JSON
Stockage persistant sur disque.

```python
from memory import set_memory_store, JSONFileStore

set_memory_store(JSONFileStore("./data"))
```

## 🌐 Interface Web de Monitoring

Le système inclut une interface web complète pour monitorer et configurer les agents.

### Lancement de l'Interface Web

```bash
python run_web.py
```

Puis ouvrez votre navigateur sur http://localhost:8000

### Fonctionnalités de l'Interface

| Section | Description |
|---------|-------------|
| **Dashboard** | Vue d'ensemble : sessions, conversions, scores moyens |
| **Sessions** | Liste et détail de toutes les conversations |
| **Logs Agents** | Historique des actions de chaque agent en temps réel |
| **Blackboard** | Mémoire partagée et insights collectés |
| **Prompts** | Modification des prompts système de chaque agent |
| **Configuration** | Choix du provider LLM (OpenAI, Claude, Grok, DeepSeek) et connexions MCP |
| **Nouveau Prospect** | Formulaire d'insertion manuelle de prospects |

### Configuration LLM

Changez de provider LLM dynamiquement :
- **OpenAI** : GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo
- **Anthropic** : Claude 3.5 Sonnet, Claude 3 Opus
- **Grok (xAI)** : Grok 2, Grok Beta
- **DeepSeek** : DeepSeek Chat, DeepSeek Coder

### Connexions MCP

Gérez les intégrations externes :
- **HubSpot CRM** : Synchronisation des contacts et deals
- **Gmail** : Envoi d'emails automatisés
- **Google Drive** : Stockage de documents
- **Accès Web** : Recherche internet
- **LinkedIn** : Prospection sociale

### API REST

L'interface web expose une API REST complète :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/sessions` | GET | Liste des sessions |
| `/api/sessions/{id}` | GET | Détail d'une session |
| `/api/logs` | GET | Logs des agents |
| `/api/blackboard` | GET | État de la mémoire partagée |
| `/api/prompts` | GET | Tous les prompts |
| `/api/prompts/{agent}` | GET/PUT | Prompt d'un agent |
| `/api/config` | GET/PUT | Configuration système |
| `/api/prospects` | POST | Créer un prospect |
| `/api/prospects/{id}/message` | POST | Envoyer un message |

Documentation Swagger : http://localhost:8000/docs

## 📁 Structure du Projet

```
AgenticSellerPOC/
├── agents/              # Agents spécialisés
│   ├── __init__.py
│   ├── base.py         # Classe de base
│   ├── classifier.py   # Qualification prospects
│   ├── seller.py       # Création d'offres
│   ├── negotiator.py   # Gestion objections
│   ├── crm.py          # Intégration CRM
│   └── supervisor.py   # Supervision processus
├── web/                 # Interface web de monitoring
│   ├── app.py          # Application FastAPI
│   ├── models.py       # Modèles Pydantic API
│   ├── templates/      # Templates HTML
│   └── static/         # Fichiers statiques
├── config.py           # Configuration
├── state.py            # Gestion d'état
├── memory.py           # Stockage mémoire
├── orchestrator.py     # Orchestrateur LangGraph
├── main.py             # Point d'entrée CLI
├── run_web.py          # Point d'entrée Web
├── examples.py         # Scénarios d'exemple
├── requirements.txt    # Dépendances Python
└── README.md           # Ce fichier
```

## 📞 Contact IAfluence

**Suan Tay** - Fondateur & Consultant

- 📧 Email : suan.tay@iafluence.fr
- 📱 Téléphone : 06 65 19 76 33
- 📅 Calendrier : https://calendar.app.google/BcE52KKmVRmki1kZ8

---

## 🛠️ Développement

### Ajouter un Nouvel Agent

1. Créer un fichier dans `agents/`
2. Hériter de `BaseAgent`
3. Implémenter la méthode `process(state)`
4. Ajouter au graphe dans `orchestrator.py`
5. Mettre à jour la logique de routage dans le MCP

### Étendre l'État

Ajouter de nouveaux champs à `SalesState` dans `state.py` :

```python
class SalesState(TypedDict):
    # ... champs existants ...
    votre_nouveau_champ: VotreType
```

## 🧪 Tests

Lancer différents scénarios pour tester le comportement des agents :

```bash
# Tester la qualification
python main.py scenario pme_shadow_ia

# Tester la négociation
python main.py scenario objection_budget

# Tester l'escalade
python main.py scenario escalade_grand_compte
```

## 📈 Évolutions Futures

- [ ] Intégration base vectorielle pour mémoire sémantique
- [ ] Intégration CRM réelle (HubSpot, Salesforce)
- [ ] Dashboard analytics
- [ ] Intégration email/SMS automatique
- [ ] Webhook temps réel
- [ ] A/B testing des offres

## 🙏 Technologies

Construit avec :
- [LangGraph](https://github.com/langchain-ai/langgraph) - Orchestration multi-agents
- [LangChain](https://github.com/langchain-ai/langchain) - Framework LLM
- [OpenAI GPT-4](https://openai.com) - Modèle de langage
- [Anthropic Claude](https://anthropic.com) - LLM alternatif

---

**IAfluence** - L'IA utile, au bon endroit, au bon rythme.
