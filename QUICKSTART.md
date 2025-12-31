# 🚀 Guide de démarrage rapide

Guide rapide pour lancer l'agent de vente en 5 minutes.

## ⚡ Installation express

```bash
# 1. Cloner le repo
git clone <repo-url>
cd AgenticSellerPOC

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les clés API
cp .env.example .env
nano .env  # Ajouter votre OPENAI_API_KEY ou ANTHROPIC_API_KEY
```

## 🎮 Première utilisation

### Option 1 : Mode interactif (recommandé)

Lancez une conversation interactive :

```bash
python main.py demo
```

Vous pourrez discuter avec l'agent comme un vrai prospect.

**Exemple de conversation :**

```
👤 You: Hi, I'm looking for a CRM for my 30-person startup
🔍 CLASSIFIER: [Analyse le lead...]
💼 SELLER: Based on your needs, I recommend...
👤 You: Sounds good but a bit expensive
🤝 NEGOTIATOR: I understand. Let me offer...
```

### Option 2 : Scénarios pré-définis

Testez avec des scénarios pré-programmés :

```bash
# PME avec usage ChatGPT non contrôlé
python main.py scenario pme_shadow_ia

# Négociation budgétaire
python main.py scenario objection_budget

# Deal enterprise complexe
python main.py scenario escalade_grand_compte

# Conversion rapide
python main.py scenario conversion_rapide
```

## 📋 Scénarios disponibles

10 scénarios de vente IAfluence réalistes :

| Scénario | Description | Complexité |
|----------|-------------|-----------|
| `pme_shadow_ia` | PME avec usage ChatGPT non contrôlé | ⭐⭐ Moyen |
| `eti_strategie_ia` | ETI cherchant stratégie IA complète | ⭐⭐⭐ Avancé |
| `formation_dirigeants` | Formation pour dirigeants | ⭐ Simple |
| `poc_souverain` | POC pour solution souveraine | ⭐⭐⭐ Avancé |
| `objection_budget` | Négociation budgétaire | ⭐⭐ Moyen |
| `objection_timing` | Objection "pas maintenant" | ⭐⭐ Moyen |
| `lead_froid` | Lead froid en recherche | ⭐ Simple |
| `escalade_grand_compte` | Deal enterprise complexe | ⭐⭐⭐ Avancé |
| `conversion_rapide` | Conversion rapide motivée | ⭐ Simple |
| `accompagnement_global` | Accompagnement multi-mois | ⭐⭐⭐ Avancé |

Liste complète avec descriptions :
```bash
python main.py list
```

## 🔑 Configuration minimale

Fichier `.env` minimum :

```bash
# === LLM Configuration (choisir UN provider) ===
OPENAI_API_KEY=sk-...                    # Pour GPT-4
# OU
ANTHROPIC_API_KEY=sk-ant-...             # Pour Claude

# Modèle par défaut
DEFAULT_LLM_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_ITERATIONS=10

# === CRM Intégrations (optionnel) ===
HUBSPOT_API_KEY=your-hubspot-key
SALESFORCE_API_KEY=your-salesforce-key

# === Storage (optionnel) ===
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key
REDIS_URL=redis://localhost:6379/0

# === Web Auth (requis pour l'interface web) ===
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
SECRET_KEY=your-secret-session-key
AUTHORIZED_EMAILS=email1@example.com,email2@example.com
APP_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./data/users.db
```

## 🧪 Test rapide

Vérifiez que tout fonctionne :

```python
from orchestrator import SalesOrchestrator

# Créer l'orchestrateur
orchestrator = SalesOrchestrator()

# Tester une conversation simple
state = orchestrator.run_conversation(
    "Hi, I need a CRM for my small team of 10 people"
)

# Vérifier le résultat
print(f"Lead Score: {state['lead_score']}/100")
print(f"Qualified: {state['qualified']}")
```

## 📊 Comprendre les résultats

Après chaque conversation, vous verrez :

```
📊 CONVERSATION SUMMARY
Session ID: abc-123-def
Lead Type: warm                    ← hot/warm/cold
Lead Score: 75/100                 ← 0-100
Qualified: ✅ Yes                  ← Qualifié ou non
Converted: ❌ No                   ← A acheté ?
Escalated: ❌ No                   ← Besoin humain ?
Messages Exchanged: 8              ← Nombre messages
Offers Made: 2                     ← Nombre offres
Negotiation Rounds: 1              ← Rounds négo
```

## 🎯 Cas d'usage typiques

### Cas 1 : Tester la qualification

```bash
python main.py demo
# Entrez : "Je cherche juste des infos, pas de budget pour l'instant"
# Résultat : Lead froid, non qualifié
```

### Cas 2 : Tester la négociation

```bash
python main.py scenario objection_budget
# Observe comment l'agent ajuste l'offre et propose des facilités de paiement
```

### Cas 3 : Tester l'escalade

```bash
python main.py scenario escalade_grand_compte
# Vois quand l'agent escalade vers un humain pour un deal complexe
```

### Cas 4 : Tester la conversion rapide

```bash
python main.py scenario conversion_rapide
# Observe une conversion rapide d'un lead chaud très motivé
```

## 🔧 Personnalisation rapide

### Changer les services offerts

Éditez `agents/seller.py`, section "Available products" :

```python
Available products:
1. DIAGNOSTIC
   - Gratuit ou 490€ (version premium)

2. STRATEGIE IA & GOUVERNANCE
   - À partir de 3,500€

3. FORMATION & MONTÉE EN COMPÉTENCES
   - À partir de 1,500€/jour

4. EXPERTISE TECHNIQUE & POC
   - À partir de 5,000€

5. ACCOMPAGNEMENT GLOBAL
   - À partir de 2,500€/mois
```

### Modifier les règles de négociation

Éditez `agents/negotiator.py` :

```python
# Maximum discount
- Maximum discount: 30% → Changez à 40%

# Nombre max de rounds
if negotiation_count >= 3: → Changez à 5
```

### Ajuster le scoring

Éditez `agents/classifier.py`, section "Classification criteria".

## 🐛 Troubleshooting

### Erreur : "No API key found"

```bash
# Vérifiez que .env existe et contient :
OPENAI_API_KEY=sk-...
# OU
ANTHROPIC_API_KEY=sk-ant-...
```

### Erreur : "Module not found"

```bash
# Réinstallez les dépendances
pip install -r requirements.txt
```

### LLM ne répond pas

```bash
# Vérifiez votre clé API
python -c "from config import config; print(config.openai_api_key)"

# Testez manuellement
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Réponses incohérentes

- Augmentez la température : `TEMPERATURE=0.8` dans `.env`
- Changez le modèle : `DEFAULT_LLM_MODEL=gpt-4-turbo-preview`

## 📚 Prochaines étapes

Une fois familiarisé :

1. **Lire l'architecture** : `ARCHITECTURE.md` pour comprendre le fonctionnement interne
2. **Créer vos scénarios** : Ajoutez dans `examples.py`
3. **Personnaliser les agents** : Modifiez les prompts et règles
4. **Intégrer au CRM** : Connectez à votre vrai CRM (voir `agents/crm.py`)
5. **Déployer** : Créez une API Flask/FastAPI autour de l'orchestrateur

## 🎓 Ressources

- **README.md** : Documentation complète
- **ARCHITECTURE.md** : Détails techniques
- **examples.py** : Tous les scénarios
- **agents/** : Code de chaque agent

## 💡 Exemples de messages à tester

**Lead chaud :**
```
"Je suis le PDG d'une PME de 50 personnes. On utilise ChatGPT partout sans contrôle et j'ai besoin d'une stratégie IA rapidement. Budget de 5000€/mois disponible."
```

**Lead tiède :**
```
"On s'intéresse à l'IA générative pour notre service client. On aimerait en savoir plus sur vos formations."
```

**Lead froid :**
```
"Je regarde juste ce qui existe en matière d'IA, pas de besoin immédiat."
```

**Objection budget :**
```
"Ça a l'air intéressant mais notre budget est limité à 2000€ pour le moment."
```

**Objection timing :**
```
"C'est intéressant mais on préfère attendre le prochain trimestre pour lancer ça."
```

**Objection autorité :**
```
"Je dois en parler avec mon comité de direction avant de décider."
```

**Conversion :**
```
"Parfait, exactement ce qu'il nous faut ! On peut démarrer quand ?"
```

---

**Bon test ! 🚀**
