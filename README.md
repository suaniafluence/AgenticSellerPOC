# AgenticSellerPOC

[![CI Pipeline](https://github.com/suaniafluence/AgenticSellerPOC/workflows/CI%20Pipeline/badge.svg)](https://github.com/suaniafluence/AgenticSellerPOC/actions)
[![codecov](https://codecov.io/gh/suaniafluence/AgenticSellerPOC/branch/main/graph/badge.svg)](https://codecov.io/gh/suaniafluence/AgenticSellerPOC)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Agentic Seller Proof of Concept

## Features

- 🚀 Modern Python project structure
- 🔄 Complete CI/CD pipeline with GitHub Actions
- 🧪 Automated testing with pytest
- 📦 Docker support
- 🔒 Security scanning with Bandit and CodeQL
- 📊 Code coverage tracking
- 🎨 Code formatting with Black and Ruff

## Installation

### Using pip

```bash
pip install agenticsellerpoc
```

### From source

```bash
git clone https://github.com/suaniafluence/AgenticSellerPOC.git
cd AgenticSellerPOC
pip install -r requirements.txt
pip install -e .
```

### Using Docker

```bash
docker build -t agenticsellerpoc .
docker run agenticsellerpoc
```

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/suaniafluence/AgenticSellerPOC.git
cd AgenticSellerPOC
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agenticseller --cov-report=html

# Run specific test file
pytest tests/test_example.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy .

# Security scan
bandit -r agenticseller/
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

### Continuous Integration (CI)

The CI pipeline runs on every push and pull request:

- **Linting & Formatting**: Checks code style with Ruff, Black, and isort
- **Type Checking**: Static type analysis with mypy
- **Testing**: Runs test suite across Python 3.9, 3.10, 3.11, and 3.12
- **Code Coverage**: Generates coverage reports and uploads to Codecov
- **Security Scanning**:
  - Bandit for Python security issues
  - Safety for dependency vulnerabilities
  - CodeQL for advanced security analysis
- **Build**: Validates package building

### Continuous Deployment (CD)

Automated deployment workflows:

- **PyPI Deployment**: Publishes to PyPI on release
- **Docker Images**: Builds and pushes to GitHub Container Registry
- **Environment Deployments**:
  - Staging: Auto-deploy from `develop` branch
  - Production: Deploy from releases or manually trigger

### Additional Automations

- **Dependency Updates**: Dependabot automatically creates PRs for dependency updates
- **PR Labeling**: Automatic labeling based on file changes and PR size
- **Dependency Review**: Security checks for new dependencies in PRs

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
├── .github/
│   ├── workflows/          # GitHub Actions workflows
│   │   ├── ci.yml         # Main CI pipeline
│   │   ├── cd.yml         # Deployment workflows
│   │   ├── codeql.yml     # Security scanning
│   │   ├── dependency-review.yml
│   │   └── pr-labeler.yml
│   ├── ISSUE_TEMPLATE/    # Issue templates
│   ├── PULL_REQUEST_TEMPLATE/
│   ├── dependabot.yml     # Dependabot configuration
│   └── labeler.yml        # PR labeling rules
├── agenticseller/         # Main package
│   └── __init__.py
├── tests/                 # Test suite
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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/suaniafluence/AgenticSellerPOC/issues) page.
