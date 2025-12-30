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
# Lead chaud qui convertit rapidement
python main.py scenario hot_lead

# Négociation sur le prix
python main.py scenario price_negotiation

# Deal enterprise complexe
python main.py scenario enterprise_escalation
```

## 📋 Scénarios disponibles

| Scénario | Description | Complexité |
|----------|-------------|-----------|
| `hot_lead` | Conversion rapide | ⭐ Simple |
| `price_negotiation` | Négociation de prix | ⭐⭐ Moyen |
| `feature_concerns` | Questions sur features | ⭐⭐ Moyen |
| `enterprise_escalation` | Deal complexe | ⭐⭐⭐ Avancé |

Liste complète :
```bash
python examples.py
```

## 🔑 Configuration minimale

Fichier `.env` minimum :

```bash
# Choisir UN des deux :
OPENAI_API_KEY=sk-...        # Pour GPT-4
# OU
ANTHROPIC_API_KEY=sk-ant-... # Pour Claude

# Optionnel :
DEFAULT_LLM_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
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
# Entrez : "Just browsing, no budget"
# Résultat : Cold lead, non qualifié
```

### Cas 2 : Tester la négociation

```bash
python main.py scenario price_negotiation
# Observe comment l'agent ajuste l'offre
```

### Cas 3 : Tester l'escalade

```bash
python main.py scenario enterprise_escalation
# Vois quand l'agent escalade vers un humain
```

## 🔧 Personnalisation rapide

### Changer les produits

Éditez `agents/seller.py`, section "Available products" :

```python
Available products:
- STARTER: $99/month - Basic features
- CUSTOM_PRODUCT: $499/month - Your features
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
"I'm the CEO, we have $1000/month budget, need to start ASAP"
```

**Lead tiède :**
```
"Interested in CRM, need to see features first"
```

**Lead froid :**
```
"Just looking around, no real need right now"
```

**Objection prix :**
```
"Sounds good but too expensive for us"
```

**Objection features :**
```
"Does it integrate with Salesforce? That's critical"
```

**Conversion :**
```
"Perfect! Let's do it, sign me up"
```

---

**Bon test ! 🚀**
