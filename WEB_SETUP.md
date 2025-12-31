# 🌐 Configuration de l'interface Web - IAfluence Agent Monitor

## Problème résolu : Erreur 500 lors de la création d'un prospect

Si vous avez rencontré l'erreur suivante lors du clic sur le bouton "Créer le prospect et démarrer le processus" :

```
INFO: 176.152.242.92:0 - "POST /api/prospects HTTP/1.1" 500 Internal Server Error
```

Ce guide vous aidera à résoudre le problème.

## Cause du problème

L'erreur 500 était causée par deux problèmes :

1. **Dépendances manquantes** : Le module `langgraph` et autres dépendances n'étaient pas installés
2. **Templates LangChain mal formés** : Les prompts système contenaient des accolades JSON non échappées

Ces problèmes ont été corrigés dans ce commit.

## Solution : Installation et configuration

### Étape 1 : Installer les dépendances

```bash
pip install -r requirements.txt
```

Cette commande installe tous les packages nécessaires incluant :
- `langgraph` - Framework pour orchestrer les agents
- `langchain` - Framework LLM
- `langchain-openai` - Intégration OpenAI
- `langchain-anthropic` - Intégration Anthropic Claude
- `fastapi` - Framework web
- Et toutes les autres dépendances

### Étape 2 : Configurer les clés API

L'application nécessite une clé API LLM pour fonctionner. Un fichier `.env` a été créé avec la configuration de base, mais vous devez y ajouter votre clé API.

#### Option A : Utiliser OpenAI (recommandé pour commencer)

1. Créez un compte sur [OpenAI Platform](https://platform.openai.com/)
2. Allez dans [API Keys](https://platform.openai.com/api-keys)
3. Créez une nouvelle clé API
4. Copiez la clé et ajoutez-la dans le fichier `.env` :

```bash
OPENAI_API_KEY=sk-...votre_clé_ici...
```

5. Le modèle par défaut est déjà configuré dans `.env` :

```bash
DEFAULT_LLM_MODEL=gpt-4-turbo-preview
```

#### Option B : Utiliser Anthropic Claude

1. Créez un compte sur [Anthropic Console](https://console.anthropic.com/)
2. Allez dans [Settings > API Keys](https://console.anthropic.com/settings/keys)
3. Créez une nouvelle clé API
4. Copiez la clé et ajoutez-la dans le fichier `.env` :

```bash
ANTHROPIC_API_KEY=sk-ant-...votre_clé_ici...
```

5. Changez le modèle dans `.env` :

```bash
DEFAULT_LLM_MODEL=claude-3-5-sonnet-20241022
```

### Étape 3 : Démarrer le serveur

Une fois les clés API configurées, lancez le serveur :

```bash
python run_web.py
```

Vous devriez voir :

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🤖 IAfluence Agent Monitor                            ║
║                                                           ║
║     Interface de monitoring et configuration              ║
║     du système d'agents commerciaux                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🚀 Démarrage du serveur sur http://localhost:8000
📊 Dashboard: http://localhost:8000
📚 API Docs: http://localhost:8000/docs

Appuyez sur Ctrl+C pour arrêter le serveur

INFO: Will watch for changes in these directories: ['/workspaces/AgenticSellerPOC']
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO: Started reloader process [xxxxx] using WatchFiles
INFO: Started server process [xxxxx]
INFO: Waiting for application startup.
🚀 Starting IAfluence Agent Monitor...
✅ Agent Monitor ready!
INFO: Application startup complete.
```

### Étape 4 : Tester la création d'un prospect

1. Ouvrez votre navigateur sur http://localhost:8000
2. Cliquez sur "Nouveau Prospect" dans le menu de gauche
3. Remplissez le formulaire avec les informations suivantes (exemple) :
   - **Nom complet** : Suan Tay
   - **Entreprise** : IAfluence
   - **Email** : suan.tay@iafluence.fr
   - **Téléphone** : 0665197633
   - **Secteur** : Autre
   - **Taille entreprise** : PME (20-249)
   - **Cochez** "Décideur (DG, DSI, DRH...)"
   - **Problématiques** : Shadow AI, Gouvernance
   - **Centres d'intérêt** : automation
   - **Notes** : Je suis le PDG d'une PME de 50 personnes. On utilise ChatGPT partout sans contrôle et j'ai besoin d'une stratégie IA rapidement. Budget de 5000€/mois disponible.
4. Cliquez sur "Créer le prospect et démarrer le processus"

Si tout est bien configuré, vous devriez voir un message de succès et le prospect sera créé avec un score de lead !

## Résolution des problèmes courants

### Erreur 500 Internal Server Error

**Symptôme** : Le bouton "Créer le prospect" retourne une erreur 500

**Causes possibles** :
1. Clé API manquante ou invalide
2. Dépendances non installées
3. Problème de connexion réseau

**Solutions** :

1. **Vérifier la clé API** :
   ```bash
   # Ouvrez le fichier .env et vérifiez que la clé est bien renseignée
   cat .env | grep API_KEY
   ```

2. **Réinstaller les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Vérifier les logs du serveur** :
   Les logs dans le terminal où vous avez lancé `python run_web.py` afficheront l'erreur exacte.

### ModuleNotFoundError: No module named 'langgraph'

**Cause** : Les dépendances Python ne sont pas installées

**Solution** :
```bash
pip install -r requirements.txt
```

### APIConnectionError: 403 Forbidden

**Cause** : Clé API invalide, expirée, ou sans crédit

**Solutions** :
1. Vérifiez que votre clé API est correcte dans `.env`
2. Vérifiez que vous avez du crédit sur votre compte API :
   - OpenAI : https://platform.openai.com/usage
   - Anthropic : https://console.anthropic.com/settings/billing
3. Vérifiez que la clé n'a pas été révoquée
4. Créez une nouvelle clé si nécessaire

### Connection timeout ou erreurs réseau

**Cause** : Problème de proxy ou de réseau

**Solution** :
Si vous êtes derrière un proxy d'entreprise, configurez les variables d'environnement :
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## Fonctionnalités de l'interface Web

### 1. Dashboard (/)

Vue d'ensemble du système avec :
- Statistiques globales (sessions actives, conversions, score moyen)
- Liste des sessions récentes
- Logs d'activité en temps réel

### 2. Sessions (/sessions)

Liste de toutes les sessions de conversation avec :
- Type de lead (chaud/tiède/froid)
- Score de lead (0-100)
- Statut (qualifié, converti, escaladé)
- Nombre de messages échangés

### 3. Nouveau Prospect (/prospects/new)

Formulaire pour créer un nouveau prospect et démarrer automatiquement le processus de vente.

### 4. Blackboard (/blackboard)

Vue en temps réel de l'état de la mémoire partagée :
- Sessions actives
- Insights collectés
- Métriques globales

### 5. Prompts (/prompts)

Interface pour visualiser et personnaliser les prompts système de chaque agent :
- Classifier
- Seller
- Negotiator
- Supervisor
- CRM

### 6. Configuration (/config)

Paramétrage du système :
- Choix du modèle LLM
- Température et paramètres
- Connexions MCP (HubSpot, Gmail, Google Drive, etc.)
- Nombre maximum d'itérations

### 7. Logs (/logs)

Logs détaillés de l'activité des agents :
- Actions effectuées
- États d'entrée/sortie
- Durée d'exécution
- Filtrage par session ou agent

## API REST

L'interface web expose une API REST documentée automatiquement :

- **Documentation interactive** : http://localhost:8000/docs
- **Schéma OpenAPI** : http://localhost:8000/openapi.json

### Endpoints principaux

- `GET /api/sessions` - Liste toutes les sessions
- `GET /api/sessions/{session_id}` - Détails d'une session
- `POST /api/prospects` - Créer un nouveau prospect
- `POST /api/prospects/{session_id}/message` - Envoyer un message
- `GET /api/logs` - Récupérer les logs
- `GET /api/blackboard` - État du blackboard
- `GET /api/prompts` - Liste des prompts
- `PUT /api/prompts/{agent_name}` - Modifier un prompt
- `GET /api/config` - Configuration système
- `PUT /api/config` - Mettre à jour la configuration

## Architecture technique

L'interface web est construite avec :
- **Backend** : FastAPI (Python)
- **Frontend** : HTML/CSS/JavaScript vanilla
- **Templates** : Jinja2
- **API** : REST avec documentation OpenAPI automatique
- **Orchestration** : LangGraph pour le workflow des agents
- **Storage** : JSON file-based pour la persistance

## Corrections apportées dans ce commit

1. **Templates LangChain corrigés** :
   - `agents/classifier.py` : Échappement des accolades JSON dans le prompt système
   - `agents/seller.py` : Échappement des accolades JSON
   - `agents/negotiator.py` : Échappement des accolades JSON
   - `agents/supervisor.py` : Échappement des accolades JSON

2. **Fichier .env créé** :
   - Configuration de base pour démarrer l'application
   - Instructions claires pour ajouter les clés API

3. **Documentation ajoutée** :
   - Ce guide de configuration web
   - Instructions de résolution des problèmes

## Prochaines étapes

Une fois que l'application fonctionne :

1. **Explorez le Dashboard** pour voir les sessions actives et les métriques
2. **Créez des prospects** et observez le comportement des agents
3. **Consultez les logs** pour comprendre le flux de décision
4. **Personnalisez les prompts** pour adapter les agents à votre cas d'usage
5. **Configurez les intégrations MCP** (HubSpot, etc.) pour connecter votre CRM

## Support et ressources

- **Documentation complète** : `README.md`
- **Guide de démarrage rapide CLI** : `QUICKSTART.md`
- **Architecture détaillée** : `ARCHITECTURE.md`
- **Code source des agents** : Dossier `agents/`
- **API FastAPI** : `web/app.py`

Si vous rencontrez d'autres problèmes, consultez les logs du serveur dans le terminal où vous avez lancé `python run_web.py`.
