# 📡 API Reference - AgenticSellerPOC

Documentation complète de l'API REST FastAPI.

## 🌐 Base URL

```
http://localhost:8000
```

## 🔐 Authentification

L'API utilise **Google OAuth 2.0** pour l'authentification.

### Configuration requise

```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
SECRET_KEY=your-secret-session-key
AUTHORIZED_EMAILS=email1@example.com,email2@example.com
```

### Endpoints d'authentification

#### Login avec Google

```http
GET /login
```

Redirige vers Google OAuth pour l'authentification.

#### Callback OAuth

```http
GET /auth/callback
```

Endpoint de callback après authentification Google.

#### Logout

```http
GET /logout
```

Déconnecte l'utilisateur et invalide la session.

---

## 📊 Sessions API

### Liste des sessions

```http
GET /api/sessions
```

Récupère la liste de toutes les sessions de vente.

**Query Parameters:**
- `limit` (optional, integer) - Nombre maximum de sessions à retourner
- `offset` (optional, integer) - Nombre de sessions à sauter

**Response:**
```json
[
  {
    "session_id": "abc-123-def",
    "timestamp": "2024-01-15T10:30:00Z",
    "lead_type": "warm",
    "lead_score": 75,
    "qualified": true,
    "converted": false,
    "escalated": false,
    "messages_count": 8
  }
]
```

### Détail d'une session

```http
GET /api/sessions/{session_id}
```

Récupère les détails complets d'une session spécifique.

**Path Parameters:**
- `session_id` (required, string) - ID unique de la session

**Response:**
```json
{
  "session_id": "abc-123-def",
  "timestamp": "2024-01-15T10:30:00Z",
  "lead_info": {
    "sector": "tech",
    "company_size": "pme",
    "maturity": "explorateur",
    "pain_points": ["shadow IT ChatGPT", "gouvernance IA"],
    "interests": ["stratégie IA", "formation"]
  },
  "lead_type": "warm",
  "lead_score": 75,
  "qualified": true,
  "converted": false,
  "escalated": false,
  "messages": [
    {
      "role": "user",
      "content": "Bonjour, nous cherchons à structurer notre usage de l'IA...",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "classifier",
      "content": "Merci pour votre message...",
      "timestamp": "2024-01-15T10:30:15Z"
    }
  ],
  "offers_made": [
    {
      "service": "STRATEGIE IA & GOUVERNANCE",
      "price": 5000,
      "discount": 0,
      "engagement_type": "trimestriel"
    }
  ],
  "objections": ["budget"],
  "negotiation_count": 1,
  "key_insights": [
    "PME tech mature",
    "Usage non contrôlé de ChatGPT"
  ]
}
```

---

## 📝 Logs API

### Récupérer les logs des agents

```http
GET /api/logs
```

Récupère l'historique des actions des agents.

**Query Parameters:**
- `session_id` (optional, string) - Filtrer par session
- `agent` (optional, string) - Filtrer par agent (classifier, seller, negotiator, supervisor, crm)
- `limit` (optional, integer) - Nombre maximum de logs
- `offset` (optional, integer) - Nombre de logs à sauter

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:15Z",
    "session_id": "abc-123-def",
    "agent": "classifier",
    "action": "qualify_lead",
    "details": {
      "lead_type": "warm",
      "lead_score": 75,
      "reasoning": "PME tech mature avec budget identifié"
    }
  },
  {
    "timestamp": "2024-01-15T10:31:00Z",
    "session_id": "abc-123-def",
    "agent": "seller",
    "action": "create_offer",
    "details": {
      "service": "STRATEGIE IA & GOUVERNANCE",
      "price": 5000
    }
  }
]
```

---

## 🧠 Blackboard API

### État de la mémoire partagée

```http
GET /api/blackboard
```

Récupère l'état global du système et les insights agrégés.

**Response:**
```json
{
  "total_sessions": 145,
  "active_sessions": 12,
  "total_conversions": 38,
  "conversion_rate": 26.2,
  "average_lead_score": 62.5,
  "insights": [
    {
      "category": "common_pain_points",
      "items": [
        {"text": "shadow IT ChatGPT", "count": 45},
        {"text": "gouvernance IA", "count": 32},
        {"text": "formation équipes", "count": 28}
      ]
    },
    {
      "category": "common_objections",
      "items": [
        {"type": "BUDGET", "count": 67},
        {"type": "TIMING", "count": 42},
        {"type": "AUTORITE", "count": 31}
      ]
    },
    {
      "category": "top_services",
      "items": [
        {"service": "STRATEGIE IA & GOUVERNANCE", "count": 52},
        {"service": "FORMATION & MONTÉE EN COMPÉTENCES", "count": 41},
        {"service": "DIAGNOSTIC", "count": 35}
      ]
    }
  ]
}
```

---

## 🎛️ Configuration API

### Récupérer la configuration

```http
GET /api/config
```

Récupère la configuration actuelle du système.

**Response:**
```json
{
  "llm_provider": "OPENAI",
  "llm_model": "gpt-4-turbo-preview",
  "temperature": 0.7,
  "max_iterations": 10,
  "mcp_connections": [
    {
      "type": "HUBSPOT",
      "enabled": false,
      "config": {}
    },
    {
      "type": "WEB",
      "enabled": true,
      "config": {}
    }
  ]
}
```

### Mettre à jour la configuration

```http
PUT /api/config
```

Met à jour la configuration du système.

**Request Body:**
```json
{
  "llm_provider": "ANTHROPIC",
  "llm_model": "claude-3-5-sonnet-20241022",
  "temperature": 0.8,
  "max_iterations": 15
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "config": {
    "llm_provider": "ANTHROPIC",
    "llm_model": "claude-3-5-sonnet-20241022",
    "temperature": 0.8,
    "max_iterations": 15
  }
}
```

### Liste des modèles LLM disponibles

```http
GET /api/config/llm-models
```

Récupère la liste des modèles LLM disponibles par provider.

**Response:**
```json
{
  "OPENAI": [
    "gpt-4-turbo-preview",
    "gpt-4",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo"
  ],
  "ANTHROPIC": [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229"
  ],
  "GROK": [
    "grok-beta",
    "grok-2"
  ],
  "DEEPSEEK": [
    "deepseek-chat",
    "deepseek-coder"
  ]
}
```

---

## 📝 Prompts API

### Liste tous les prompts

```http
GET /api/prompts
```

Récupère tous les prompts système des agents.

**Response:**
```json
{
  "classifier": "Vous êtes un expert en qualification de leads B2B...",
  "seller": "Vous êtes un consultant commercial expert...",
  "negotiator": "Vous êtes un expert en négociation commerciale...",
  "supervisor": "Vous êtes un superviseur stratégique...",
  "crm": "Vous êtes responsable de la synchronisation CRM..."
}
```

### Récupérer le prompt d'un agent

```http
GET /api/prompts/{agent_name}
```

Récupère le prompt système d'un agent spécifique.

**Path Parameters:**
- `agent_name` (required, string) - Nom de l'agent (classifier, seller, negotiator, supervisor, crm)

**Response:**
```json
{
  "agent": "classifier",
  "prompt": "Vous êtes un expert en qualification de leads B2B pour IAfluence, cabinet de conseil spécialisé en IA générative..."
}
```

### Mettre à jour le prompt d'un agent

```http
PUT /api/prompts/{agent_name}
```

Met à jour le prompt système d'un agent.

**Path Parameters:**
- `agent_name` (required, string) - Nom de l'agent

**Request Body:**
```json
{
  "prompt": "Nouveau prompt système personnalisé..."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Prompt updated successfully",
  "agent": "classifier",
  "prompt": "Nouveau prompt système personnalisé..."
}
```

---

## 👤 Prospects API

### Créer un nouveau prospect

```http
POST /api/prospects
```

Crée un nouveau prospect et démarre le processus de vente.

**Request Body:**
```json
{
  "name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "company": "TechCorp",
  "initial_message": "Bonjour, nous cherchons à structurer notre usage de l'IA dans notre entreprise de 50 personnes."
}
```

**Response:**
```json
{
  "session_id": "new-session-xyz",
  "prospect": {
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "company": "TechCorp"
  },
  "response": "Merci pour votre message Jean. Je comprends que vous cherchez à structurer l'usage de l'IA dans votre entreprise...",
  "lead_type": "warm",
  "lead_score": 65
}
```

### Envoyer un message à un prospect

```http
POST /api/prospects/{session_id}/message
```

Continue la conversation avec un prospect existant.

**Path Parameters:**
- `session_id` (required, string) - ID de la session

**Request Body:**
```json
{
  "message": "Oui, nous utilisons beaucoup ChatGPT mais sans contrôle. Notre budget est de 5000€."
}
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "response": "Je comprends parfaitement votre situation. Le Shadow IT autour de ChatGPT est un problème courant...",
  "agent": "seller",
  "offer": {
    "service": "STRATEGIE IA & GOUVERNANCE",
    "price": 5000,
    "engagement_type": "trimestriel"
  }
}
```

---

## 🏥 Health Check

### Vérifier l'état de l'API

```http
GET /health
```

Vérifie que l'API fonctionne correctement.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## 🖥️ Pages Web

### Dashboard

```http
GET /
```

Page d'accueil du dashboard web.

### Documentation Swagger

```http
GET /docs
```

Documentation interactive OpenAPI (Swagger UI).

### Documentation ReDoc

```http
GET /redoc
```

Documentation alternative au format ReDoc.

---

## 🔧 Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé avec succès |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Accès interdit (email non autorisé) |
| 404 | Ressource non trouvée |
| 422 | Erreur de validation |
| 500 | Erreur serveur interne |

## 📝 Exemples d'utilisation

### Python (requests)

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"

# Créer un prospect
response = requests.post(
    f"{BASE_URL}/api/prospects",
    json={
        "name": "Marie Martin",
        "email": "marie@example.com",
        "company": "DataCorp",
        "initial_message": "Nous cherchons une formation en IA générative"
    }
)
session = response.json()
print(f"Session ID: {session['session_id']}")

# Envoyer un message
response = requests.post(
    f"{BASE_URL}/api/prospects/{session['session_id']}/message",
    json={"message": "Notre équipe compte 30 personnes"}
)
print(response.json()['response'])
```

### JavaScript (fetch)

```javascript
// Créer un prospect
const response = await fetch('http://localhost:8000/api/prospects', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Pierre Durand',
    email: 'pierre@example.com',
    company: 'InnovateCorp',
    initial_message: 'Besoin d\'aide pour gouvernance IA'
  })
});

const session = await response.json();
console.log('Session ID:', session.session_id);

// Liste des sessions
const sessions = await fetch('http://localhost:8000/api/sessions')
  .then(res => res.json());
console.log('Total sessions:', sessions.length);
```

### cURL

```bash
# Créer un prospect
curl -X POST http://localhost:8000/api/prospects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sophie Laurent",
    "email": "sophie@example.com",
    "company": "TechStartup",
    "initial_message": "Nous voulons déployer l'\''IA dans notre PME"
  }'

# Récupérer les sessions
curl http://localhost:8000/api/sessions

# Récupérer la configuration
curl http://localhost:8000/api/config

# Mettre à jour la configuration
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "llm_provider": "ANTHROPIC",
    "llm_model": "claude-3-5-sonnet-20241022",
    "temperature": 0.8
  }'
```

---

## 🚀 Démarrage rapide de l'API

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Lancer le serveur
python run_web.py

# L'API est disponible sur http://localhost:8000
# Documentation Swagger : http://localhost:8000/docs
```

---

Pour plus d'informations, consultez :
- **README.md** - Documentation générale
- **ARCHITECTURE.md** - Architecture du système
- **QUICKSTART.md** - Guide de démarrage rapide
