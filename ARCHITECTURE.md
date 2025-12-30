# 🏗️ Architecture détaillée - Agent de vente multicanal

Ce document décrit l'architecture complète du système multi-agents de vente adaptatif.

## 📐 Vue d'ensemble de l'architecture

### Principe MCP (Multi-Agent Control Plane)

Le MCP est une architecture qui centralise la logique de décision et de routage dans un nœud de contrôle unique, plutôt que de laisser les agents se coordonner directement entre eux.

**Avantages du MCP :**
- ✅ Contrôle centralisé du flux d'exécution
- ✅ État global cohérent et synchronisé
- ✅ Traçabilité complète de toutes les décisions
- ✅ Facilité de modification des règles métier
- ✅ Debugging et monitoring simplifiés
- ✅ Évite les boucles infinies entre agents

### Architecture en couches

```
┌────────────────────────────────────────────────────────┐
│                   Layer 1: Interface                    │
│                  (main.py, CLI, API)                   │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│              Layer 2: Orchestration                     │
│          (orchestrator.py - LangGraph MCP)             │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │         MCP Decision Node                     │    │
│  │  - Analyse de l'état                         │    │
│  │  - Routage conditionnel                      │    │
│  │  - Détection de conversion/escalade          │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│               Layer 3: Agents                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │Classifier│ │  Seller  │ │Negotiator│ │Supervisor│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                    ┌──────────┐                        │
│                    │   CRM    │                        │
│                    └──────────┘                        │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│            Layer 4: State & Memory                      │
│  ┌────────────────┐  ┌────────────────┐               │
│  │  SalesState    │  │  Memory Store  │               │
│  │  (state.py)    │  │  (memory.py)   │               │
│  └────────────────┘  └────────────────┘               │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│              Layer 5: LLM & External                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ OpenAI/    │  │    CRM     │  │  Vector    │       │
│  │ Anthropic  │  │   APIs     │  │    DB      │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└────────────────────────────────────────────────────────┘
```

## 🔄 Flux d'exécution détaillé

### 1. Initialisation d'une conversation

```python
# 1. Création de l'état initial
state = create_initial_state(initial_message, session_id)

# 2. Structure de l'état
{
    "messages": [],                    # Historique complet
    "current_message": "...",          # Message actuel
    "lead_info": {...},                # Infos prospect
    "lead_type": None,                 # hot/warm/cold
    "lead_score": 0,                   # Score 0-100
    "current_agent": "start",          # Agent actif
    "offers_made": [],                 # Offres proposées
    "objections": [],                  # Objections levées
    "negotiation_count": 0,            # Nombre de négociations
    "qualified": False,                # Lead qualifié ?
    "converted": False,                # Converti ?
    "escalated": False,                # Escaladé ?
    "closed": False,                   # Terminé ?
    "next_action": None,               # Prochaine action
    ...
}
```

### 2. Routage MCP

Le nœud MCP (`_mcp_decision_node`) applique cette logique :

```python
def _mcp_decision_node(state: SalesState) -> SalesState:
    # Règle 1 : Première interaction → Classification
    if not state.get("lead_type"):
        state["next_action"] = "classifier"
        return state

    # Règle 2 : Conversation terminée → Fin
    if state.get("closed"):
        state["next_action"] = "end"
        return state

    # Règle 3 : Conversion détectée → CRM
    if self._check_for_conversion(state):
        state["converted"] = True
        state["next_action"] = "crm"
        return state

    # Règle 4 : Escalade nécessaire → CRM
    if state.get("escalated"):
        state["next_action"] = "crm"
        return state

    # Règle 5 : Suivre l'action suggérée par l'agent précédent
    next_action = state.get("next_action")

    # Règle 6 : Pas d'action définie → Demander au Supervisor
    if not next_action or next_action == "wait_for_response":
        state["next_action"] = "supervisor"

    return state
```

### 3. Exécution d'un agent

Chaque agent suit ce pattern :

```python
def process(self, state: SalesState) -> SalesState:
    # 1. Extraire le contexte de l'état
    current_message = state.get("current_message")
    conversation_history = state.get("messages")

    # 2. Créer le prompt spécialisé
    prompt = self.create_specialized_prompt()

    # 3. Appeler le LLM
    response = self.llm.invoke(prompt_data)

    # 4. Parser la réponse (JSON structuré)
    parsed = parse_json_response(response)

    # 5. Mettre à jour l'état
    state = self.update_state(state, parsed)

    # 6. Déterminer la prochaine action
    state["next_action"] = self.suggest_next_action(state)

    # 7. Retourner l'état mis à jour
    return state
```

## 🤖 Agents spécialisés

### Prospect_Classifier

**Rôle :** Qualification et scoring des leads

**Input :**
- Message initial du prospect
- Historique de conversation (si existant)

**Traitement :**
1. Analyse du message avec prompt spécialisé
2. Extraction d'informations :
   - Type de lead (hot/warm/cold)
   - Secteur d'activité (SAAS, ecommerce, etc.)
   - Taille d'entreprise (startup, SME, etc.)
   - Pain points
   - Intérêts
   - Autorité de décision
3. Calcul du score (0-100)

**Output :**
```json
{
    "lead_type": "hot",
    "sector": "saas",
    "company_size": "sme",
    "decision_maker": true,
    "pain_points": ["automation", "scaling"],
    "interests": ["api", "integrations"],
    "lead_score": 85,
    "reasoning": "...",
    "key_insights": ["..."]
}
```

**Next Action :**
- Score ≥ 50 → `seller`
- Score < 50 → `nurture`

### Seller

**Rôle :** Création d'offres personnalisées

**Input :**
- Informations du lead (classifier)
- Objections précédentes (si négociation)

**Traitement :**
1. Analyse des besoins et du budget
2. Sélection du produit approprié
3. Calcul des incentives (trial, discount)
4. Création du pitch personnalisé

**Output :**
```json
{
    "product": "PROFESSIONAL",
    "price": 299,
    "features": ["..."],
    "discount": 15,
    "trial_period": 14,
    "commitment_period": 12,
    "conditions": ["..."],
    "pitch": "Based on your needs..."
}
```

**Next Action :** `wait_for_response`

### Negotiator

**Rôle :** Gestion des objections et ajustements

**Input :**
- Message d'objection
- Offre actuelle
- Historique de négociation

**Traitement :**
1. Catégorisation de l'objection :
   - PRICE : "Trop cher"
   - FEATURES : "Manque X fonctionnalité"
   - TIMING : "Pas maintenant"
   - AUTHORITY : "Besoin d'approbation"
   - COMPETITION : "Concurrent moins cher"
   - TRUST : "Besoin de preuve"

2. Stratégie de réponse :
   - Prix : discount conditionnel, paiement échelonné
   - Features : upsell, roadmap, alternatives
   - Timing : urgence, offre limitée
   - Autorité : matériel de vente, demo

3. Ajustement de l'offre (dans les limites)

**Output :**
```json
{
    "objection_category": "PRICE",
    "adjusted_offer": {...},
    "response": "I understand your budget concerns...",
    "should_escalate": false
}
```

**Next Action :**
- Négociation count < 3 → `wait_for_response`
- Négociation count ≥ 3 → `escalate`

### Supervisor

**Rôle :** Analyse et routage stratégique

**Input :**
- État complet de la conversation
- Contexte et métriques

**Traitement :**
1. Analyse du sentiment
2. Calcul de probabilité de conversion
3. Détection de signaux :
   - Conversion immédiate
   - Besoin de négociation
   - Nécessité d'escalade
   - Fin de conversation

**Output :**
```json
{
    "analysis": "...",
    "prospect_sentiment": "positive",
    "goal_achieved": false,
    "conversion_probability": 70,
    "next_agent": "seller",
    "should_escalate": false,
    "should_close": false,
    "reasoning": "..."
}
```

**Next Action :** Décision basée sur l'analyse

### CRM_Agent

**Rôle :** Synchronisation et finalisation

**Input :**
- État complet final

**Traitement :**
1. Création du record CRM
2. Génération de tâches pour l'équipe
3. Sauvegarde de la session
4. Extraction d'insights

**Output :**
- CRM record
- Task list
- Conversation summary

**Next Action :** `end`

## 🧠 Gestion de l'état

### Structure SalesState

```python
class SalesState(TypedDict):
    # Conversation
    messages: List[Dict]           # Historique complet
    current_message: str           # Message actuel

    # Lead
    lead_info: Dict                # Infos prospect
    lead_type: Optional[str]       # Classification
    lead_score: float              # Score 0-100

    # Processus vente
    current_agent: str             # Agent actif
    last_agent: Optional[str]      # Agent précédent
    offers_made: List[Dict]        # Offres faites
    current_offer: Optional[Dict]  # Offre active

    # Négociation
    objections: List[str]          # Objections levées
    objections_handled: List[str]  # Objections traitées
    negotiation_count: int         # Nombre de rounds

    # Status
    qualified: bool                # Qualifié ?
    converted: bool                # Converti ?
    escalated: bool                # Escaladé ?
    closed: bool                   # Terminé ?

    # Métadonnées
    session_id: str                # ID unique
    context: str                   # Contexte actuel
    next_action: Optional[str]     # Action suivante
    crm_synced: bool              # Synchro CRM ?

    # Insights
    key_insights: List[str]        # Insights clés
    sentiment: str                 # Sentiment global
```

### Évolution de l'état

**Tour 1 : Message initial**
```python
{
    "current_message": "Hi, I need a CRM...",
    "lead_type": None,              # ← Non défini
    "next_action": "classifier"     # ← MCP décide
}
```

**Tour 2 : Après classification**
```python
{
    "lead_type": "warm",            # ← Défini
    "lead_score": 65,
    "qualified": True,
    "next_action": "seller"         # ← Classifier suggère
}
```

**Tour 3 : Après offre**
```python
{
    "current_offer": {...},
    "offers_made": [offer1],
    "next_action": "wait_for_response"
}
```

**Tour 4 : Après objection**
```python
{
    "objections": ["too expensive"],
    "negotiation_count": 1,
    "next_action": "negotiator"     # ← Supervisor décide
}
```

**Tour 5 : Conversion**
```python
{
    "converted": True,
    "next_action": "crm"            # ← MCP détecte
}
```

## 💾 Système de mémoire

### Architecture de mémoire

```
┌─────────────────────────────────────────────┐
│           Memory Store Interface            │
│  (Abstract: save_session, load_session)     │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
┌────▼──────┐         ┌─────▼──────┐
│ InMemory  │         │ JSONFile   │
│  Store    │         │   Store    │
│           │         │            │
│ - Fast    │         │ - Persist  │
│ - Testing │         │ - Simple   │
└───────────┘         └────────────┘

     Future:
┌─────────────┐
│  Vector DB  │
│   Store     │
│             │
│ - Semantic  │
│ - Scalable  │
└─────────────┘
```

### Opérations mémoire

```python
# Sauvegarde de session
memory.save_session(session_id, state)

# Chargement de session
state = memory.load_session(session_id)

# Sauvegarde d'insight
memory.save_insight(session_id, "Lead from SAAS sector")

# Requête d'insights
insights = memory.get_insights({"session_id": "..."})
```

## 🔀 Graphe LangGraph

### Définition du graphe

```python
workflow = StateGraph(SalesState)

# Nœuds
workflow.add_node("mcp_decision", mcp_decision_node)
workflow.add_node("classifier", classifier_node)
workflow.add_node("seller", seller_node)
workflow.add_node("negotiator", negotiator_node)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("crm", crm_node)

# Point d'entrée
workflow.set_entry_point("mcp_decision")

# Edges conditionnels depuis MCP
workflow.add_conditional_edges(
    "mcp_decision",
    route_from_mcp,  # Fonction de routage
    {
        "classifier": "classifier",
        "seller": "seller",
        "negotiator": "negotiator",
        "supervisor": "supervisor",
        "crm": "crm",
        "end": END,
    }
)

# Retour vers MCP (tous sauf CRM)
for node in ["classifier", "seller", "negotiator", "supervisor"]:
    workflow.add_edge(node, "mcp_decision")

# CRM → END (terminal)
workflow.add_edge("crm", END)
```

### Visualisation du flux

```
START
  ↓
[MCP Decision] ←──────────┐
  ├─→ [Classifier] ────────┤
  ├─→ [Seller] ────────────┤
  ├─→ [Negotiator] ────────┤
  ├─→ [Supervisor] ────────┤
  ├─→ [CRM] → END
  └─→ END
```

## 🎯 Détection de conversion

### Signaux de conversion

```python
def _check_for_conversion(state):
    message = state["current_message"].lower()

    # Mots-clés positifs
    keywords = [
        "yes", "sure", "ok", "let's do it",
        "sign me up", "i'll take it", "deal",
        "agreed", "accept", "proceed"
    ]

    return any(kw in message for kw in keywords)
```

### Métriques complémentaires

- Sentiment positif
- Score élevé
- Pas d'objections récentes
- Question sur les prochaines étapes

## 🚨 Logique d'escalade

### Critères d'escalade

1. **Trop de négociations** : `negotiation_count >= 3`
2. **Demande explicite** : "Can I speak to a human?"
3. **Deal complexe** : Enterprise avec requirements custom
4. **Budget élevé** : > $10,000/an
5. **Objections non résolues** : Pattern répétitif

### Processus d'escalade

```python
if should_escalate:
    state["escalated"] = True
    state["next_action"] = "crm"

    # CRM crée une tâche prioritaire
    task = {
        "priority": "HIGH",
        "type": "ESCALATION",
        "reason": escalation_reason,
        "assign_to": "senior_sales_rep",
        "due": "within_24h"
    }
```

## 📊 Insights et Analytics

### Données capturées

```python
crm_record = {
    "session_id": "...",
    "timestamp": "...",
    "lead_info": {...},
    "lead_type": "hot",
    "lead_score": 85,
    "qualified": True,
    "converted": True,
    "offers_made": [...],
    "objections": [...],
    "negotiation_rounds": 2,
    "key_insights": [
        "Strong interest in API integrations",
        "Budget approved, decision-maker",
        "Competitor comparison with X"
    ],
    "sentiment": "positive"
}
```

### Analyses possibles

- **Taux de conversion** par lead_type, sector, company_size
- **Objections communes** par segment
- **Patterns de négociation** efficaces
- **Temps moyen** de conversion
- **Scores moyens** par source

## 🔧 Configuration avancée

### Personnalisation des agents

```python
# Changer le modèle LLM
classifier = ProspectClassifier(
    model="gpt-4-turbo-preview",
    temperature=0.5
)

# Ou utiliser Claude
seller = SellerAgent(
    model="claude-3-opus-20240229",
    temperature=0.7
)
```

### Ajout de règles métier

```python
def custom_mcp_rule(state):
    # Règle custom : VIP fast-track
    if state["lead_score"] >= 90:
        state["next_action"] = "vip_agent"
    return state
```

### Extension du state

```python
class ExtendedSalesState(SalesState):
    vip_status: bool
    referral_source: str
    custom_field: Any
```

## 🧪 Tests et validation

### Scénarios de test

1. **Conversion rapide** : Hot lead → Seller → Accept
2. **Négociation simple** : Warm → Seller → Objection → Negotiator → Accept
3. **Escalade** : Complex → Multiple negotiations → Escalate
4. **Abandon** : Cold → Not interested → Nurture

### Métriques de qualité

- Taux de qualification correct (precision/recall)
- Pertinence des offres
- Résolution d'objections
- Taux d'escalade approprié

---

Cette architecture assure :
- ✅ **Modularité** : Agents indépendants et réutilisables
- ✅ **Contrôle** : Logique centralisée dans le MCP
- ✅ **Traçabilité** : État complet à chaque étape
- ✅ **Évolutivité** : Facile d'ajouter de nouveaux agents
- ✅ **Robustesse** : Gestion d'erreur et fallbacks
