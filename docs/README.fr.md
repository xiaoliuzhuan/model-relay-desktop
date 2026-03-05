# Model Relay Desktop

<picture>
    <img alt="Model Relay Desktop" src="../icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](../README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](README.fr.md) [![Documentação em Português (Brasil)](https://img.shields.io/badge/docs-Português-purple)](README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](README.ru.md)

## Introduction

Model Relay Desktop est une solution basée sur un proxy local pour fournisseurs de modèles fixes d'IDE, compatible avec Windows et macOS.

**Note : Ce projet ne prend actuellement en charge que les API au format openai, veuillez le confirmer. Les autres formats peuvent être convertis au format openai avant utilisation.**

<details>
  <summary>Tu ne vois rien~~</summary>
  <br>
  <p>Model Relay Desktop: local model relay desktop tool.</p>
 </details>

## Table des matières

- [Model Relay Desktop](#model-relay-desktop)
  - [Introduction](#introduction)
  - [Table des matières](#table-des-matières)
  - [Journal des modifications](#journal-des-modifications)
    - [v1.2.0 (Dernier)](#v120-dernier)
    - [v1.1.1](#v111)
    - [v1.1.0](#v110)
    - [v1.0.0](#v100)
  - [Démarrage rapide](#démarrage-rapide)
    - [Utilisateurs Windows (méthode de lancement en un clic via l'interface graphique)](#utilisateurs-windows-méthode-de-lancement-en-un-clic-via-linterface-graphique)
    - [Utilisateurs macOS (installation via l'application)](#utilisateurs-macos-installation-via-lapplication)
      - [Méthode d'installation](#méthode-dinstallation)
      - [Mode d'emploi](#mode-demploi)
  - [macOS Résolution du problème « Le paquet est corrompu »](#macos-résolution-du-problème--le-paquet-est-corrompu-)
    - [Solution graphique](#solution-graphique)
    - [Solution en ligne de commande (cli)](#solution-en-ligne-de-commande-cli)
  - [Lancement par script](#lancement-par-script)
    - [Étape 0 : Préparation de l'environnement](#étape-0--préparation-de-lenvironnement)
      - [Windows](#windows)
        - [Étape 1 : Générer un certificat auto-signé](#étape-1--générer-un-certificat-auto-signé)
        - [Étape 2 : Faire confiance à votre certificat d'autorité de certification sous Windows](#étape-2--faire-confiance-à-votre-certificat-dautorité-de-certification-sous-windows)
        - [Étape 3 : Modifier le fichier Hosts](#étape-3--modifier-le-fichier-hosts)
        - [Étape 4 : Exécuter le serveur proxy local (Python)](#étape-4--exécuter-le-serveur-proxy-local-python)
        - [Étape 5 : Configurer Trae IDE](#étape-5--configurer-trae-ide)
      - [macOS](#macos)
  - [😎 Restez à jour](#-restez-à-jour)
  - [Références](#références)

---

## Journal des modifications

### v1.2.0 (Dernier)

- 🔄 **Refonte de l'architecture de mapping des modèles** - Passage du "mapping un-à-un" à une architecture de "modèle de mapping unifié"
  - Le client trae utilise un ID de modèle de mapping unifié, MTGA bascule le modèle backend réel via le groupe de configuration
  - Le serveur proxy supporte le mapping des IDs de modèle et la validation d'authentification MTGA
  - La configuration globale prend en charge la définition de l'ID du modèle de mapping et de la clé d'authentification MTGA
- ⚡ **Optimisation de la gestion des groupes de configuration** - Refonte des champs et de la logique de validation des groupes de configuration
  - Le nom du groupe de configuration devient optionnel, l'URL API, l'ID réel du modèle et la clé API deviennent obligatoires
  - Suppression du champ d'ID du modèle cible, remplacé par une configuration de mapping globale
  - Renommage des en-têtes des groupes de configuration, rétrocompatibilité avec les anciens fichiers de configuration
- 🧪 **Ajout d'une fonctionnalité de tests automatisés** - Système complet de test de connexion aux modèles
  - Test automatique de la connexion au modèle après sauvegarde de la configuration (GET `/v1/models/{id du modèle}`)
  - Fonction de test manuel de disponibilité, support des tests de complétion de chat (POST `/v1/chat/completions`)
  - Journal détaillé des tests, incluant le contenu des réponses et le décompte des tokens consommés
- 🎯 **Amélioration de l'expérience utilisateur** - Ajout d'un bouton de test de disponibilité et d'infobulles détaillées
  - Le bouton de test de disponibilité supporte les infobulles explicatives, indiquant les risques de consommation de tokens
  - Tests asynchrones pour éviter le blocage de l'interface utilisateur, gestion complète des erreurs
  - Affichage sécurisé de la clé API (masquage)

<details>
<summary>Versions historiques</summary>

### v1.1.1

- 🐛 **Correction d'un problème avec la fonction de modification des hosts** - Résolution d'un problème de caractère de saut de ligne anormal lors de la modification du fichier hosts

### v1.1.0

- ✨ **Nouvelle fonctionnalité de gestion des données utilisateur** - La version monofichier prend en charge le stockage persistant des données utilisateur
  - Emplacement de stockage des données : Windows `%APPDATA%\MTGA\`, macOS/Linux `~/.mtga/`
  - Prise en charge de la sauvegarde, de la restauration et de l'effacement des données utilisateur
  - Configuration, certificats SSL, sauvegarde des hosts automatiquement persistants
- 🔧 **Optimisation de la construction monofichier** - Amélioration de `build_onefile.bat`, prise en charge de la variable de numéro de version
- 🎯 **Amélioration de l'interface utilisateur** - Ajout d'un bouton d'actualisation de la liste des groupes de configuration, optimisation de la mise en page de l'interface
- 📖 **Documentation améliorée** - Ajout d'un guide de construction monofichier, mise à jour de la documentation du projet

### v1.0.0

- ✅ **Adaptation pour Mac OS** - Prise en charge de l'installation d'applications macOS
- 🔄 **Changement de fournisseur par défaut** - Passage de DeepSeek à OpenAI
- 📦 **Refactorisation des fichiers** - Renommage des fichiers liés à ds au format `*_ds.*` pour archivage
- 🌐 **Modification du format de l'URL de l'API** - Passage de `https://your-api.example.com/v1` à `https://your-api.example.com`

</details>

---

## Démarrage rapide

### Utilisateurs Windows (méthode de lancement en un clic via l'interface graphique)

1. Téléchargez la dernière version de `MTGA_GUI-v{numéro de version}-x64.exe` depuis [GitHub Releases](https://github.com/xiaoliuzhuan/model-relay-desktop/releases)
2. Double-cliquez sur le fichier exe téléchargé (des privilèges d'administrateur sont requis)
3. Dans l'interface graphique ouverte, renseignez l'URL de l'API et l'ID du modèle
   - **L'URL de l'API ne nécessite que le domaine (le numéro de port est optionnel, ne le renseignez pas si vous ne comprenez pas), sans la route suivante, par exemple : `https://your-api.example.com`**
   - **Si vous souhaitez activer les capacités multimodales, vous pouvez mapper le nom du modèle vers un nom de modèle multimodal intégré :**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
4. Cliquez sur le bouton "Lancer tous les services en un clic"
5. Attendez que le programme termine automatiquement les opérations suivantes :
   - Génération et installation du certificat
   - Modification du fichier hosts
   - Démarrage du serveur proxy
6. Une fois terminé, configurez votre IDE selon [Étape 5 : Configuration de Trae IDE](#第-5-步配置-trae-ide)

> [!NOTE]
>
> - Un accès au pare-feu peut être requis lors du premier lancement
> - La version mono-fichier prend en charge la persistance des données utilisateur, la configuration et les certificats sont sauvegardés automatiquement

### Utilisateurs macOS (installation via l'application)

#### Méthode d'installation

1. Téléchargez la dernière version de `MTGA_GUI-v{numéro de version}-aarch64.dmg` depuis [GitHub Releases](https://github.com/xiaoliuzhuan/model-relay-desktop/releases)
2. Double-cliquez sur le fichier DMG, le système montera automatiquement le package d'installation
3. Glissez-déposez `MTGA_GUI.app` dans le dossier `Applications`
4. Lancez l'application depuis le Launchpad ou le dossier Applications

#### Mode d'emploi

1. Lancez `MTGA_GUI.app` (la première exécution peut nécessiter une autorisation dans les préférences système)
2. Dans l'interface graphique, renseignez :
   - **API URL** : l'adresse de votre service API (par exemple : `https://your-api.example.com`)
   - **Si vous souhaitez activer les capacités multimodales, vous pouvez mapper le nom du modèle vers un nom de modèle multimodal intégré :**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
3. Cliquez sur le bouton "Lancer tous les services en un clic"
4. Le programme effectuera automatiquement :
   - La génération et l'installation du certificat SSL dans le trousseau système
   - La modification du fichier `/etc/hosts` (nécessite les privilèges administrateur)
5. Vous devez manuellement approuver le certificat généré dans la fenêtre du trousseau qui s'ouvre, nommé par défaut `MTGA_CA`
6. Démarrez le serveur proxy local
7. Suivez la configuration [Trae IDE ci-dessous](#第-5-步配置-trae-ide) pour finaliser la configuration

> [!NOTE]
>
> - L'installation du certificat et la modification du fichier hosts nécessitent les droits d'administrateur.
> - En cas d'apparition du message « Le paquet est corrompu », veuillez consulter [macOS Résolution du problème « Le paquet est corrompu »](#macos-résolution-du-problème--le-paquet-est-corrompu-).

## macOS Résolution du problème « Le paquet est corrompu »

Si au lancement de `MTGA_GUI.app` ce message apparaît :

<img width="244" height="223" alt="app corrupted" src="../images/app-corrupted.png?raw=true" />

**Cliquez sur Annuler**. Puis suivez les étapes ci-dessous pour résoudre le problème :

### Solution graphique

1. Rendez-vous sur [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest) pour télécharger `Sentinel.dmg`
2. Double-cliquez sur le fichier `Sentinel.dmg`, puis faites glisser `Sentinel.app` dans le dossier `Applications`
3. Lancez `Sentinel.app` depuis le Launchpad ou le dossier Applications
4. Faites glisser `MTGA_GUI.app` de ce projet dans la fenêtre gauche de `Sentinel.app`
   - <img width="355.33" height="373.33" alt="sentinel add app" src="../images/sentinel-add-app.png?raw=true" />

`MTGA_GUI.app` sera automatiquement traité et lancé

### Solution en ligne de commande (cli)

1. Trouvez le chemin complet de `MTGA_GUI.app`, par exemple `/Applications/MTGA_GUI.app`.
2. Ouvrez l'application Terminal.
3. Exécutez la commande suivante pour signer `MTGA_GUI.app` :
   ```zsh
   xattr -d com.apple.quarantine <chemin complet de l'application>
   ```
   Cette commande supprime l'attribut étendu `com.apple.quarantine` de `MTGA_GUI.app`.
4. Lancez `MTGA_GUI.app`.

---

## Lancement par script

### Étape 0 : Préparation de l'environnement

#### Windows

- Système Windows 10 ou supérieur
- Avoir les privilèges administrateur
- Installer l'environnement Python, version 3.10 ou supérieure recommandée
- Installer Git

##### Étape 1 : Générer un certificat auto-signé

Ouvrez Git Bash :

```bash
# Accéder au répertoire ca
cd "mtga/ca"

# 1. Générer le certificat CA (ca.crt et ca.key)
./genca.sh
```

Lors de l'exécution de `./genca.sh`, il vous demandera "Do you want to generate ca cert and key? [yes/no]", saisissez `y` et appuyez sur Entrée. Ensuite, il vous sera demandé de renseigner quelques informations :

- `Country Name (2 letter code) []` : Saisissez `CN` (ou un autre code pays)
- Les autres champs (comme State, Locality, Organization, Common Name for CA) peuvent être remplis au besoin ou laissés vides, il est recommandé de mettre `X`. Le Common Name peut être `MTGA_CA` ou similaire. L'e-mail peut être laissé vide.

```bash
# 2. Générer le certificat SSL pour api.openai.com (api.openai.com.crt et api.openai.com.key)
#  Ce script utilisera les fichiers api.openai.com.subj et api.openai.com.cnf situés dans le même répertoire
./gencrt.sh api.openai.com
```

Une fois l'exécution terminée, vous trouverez les fichiers importants suivants dans le répertoire `mtga\ca` :

- `ca.crt` (votre certificat d'autorité de certification personnalisé)
- `ca.key` (votre clé privée d'autorité de certification personnalisée - **ne pas divulguer**)
- `api.openai.com.crt` (certificat SSL pour le serveur proxy local)
- `api.openai.com.key` (clé privée SSL pour le serveur proxy local - **ne pas divulguer**)

##### Étape 2 : Faire confiance à votre certificat d'autorité de certification sous Windows

1.  Localisez le fichier `mtga\ca\ca.crt`.
2.  Double-cliquez sur le fichier `ca.crt` pour ouvrir la visionneuse de certificats.
3.  Cliquez sur le bouton "Installer le certificat...".
4.  Choisissez "Utilisateur actuel" ou "Ordinateur local". Il est recommandé de choisir "Ordinateur local" (cela nécessite les privilèges administrateur) pour que cela s'applique à tous les utilisateurs.
5.  Dans la boîte de dialogue suivante, sélectionnez "Placer tous les certificats dans le magasin suivant", puis cliquez sur "Parcourir...".
6.  Sélectionnez "Autorités de certification racines de confiance", puis cliquez sur "OK".
7.  Cliquez sur "Suivant", puis "Terminer". Si un avertissement de sécurité apparaît, choisissez "Oui".

##### Étape 3 : Modifier le fichier Hosts

**⚠️ AVERTISSEMENT : Après avoir effectué cette étape, vous ne pourrez plus accéder à l'API originale d'OpenAI. L'utilisation du site web n'est pas affectée.**

Vous devez modifier le fichier Hosts avec des privilèges d'administrateur pour pointer `api.openai.com` vers votre machine locale.

1.  Chemin du fichier Hosts : `C:\Windows\System32\drivers\etc\hosts`
2.  Ouvrez ce fichier en tant qu'administrateur avec le Bloc-notes (ou un autre éditeur de texte).
3.  Ajoutez la ligne suivante à la fin du fichier :
    ```
    127.0.0.1 api.openai.com
    ```
4.  Enregistrez le fichier.

##### Étape 4 : Exécuter le serveur proxy local (Python)

**Avant d'exécuter le serveur proxy :**

1.  **Installer les dépendances**:
    ```bash
    pip install Flask requests
    ```
2.  **Configurer le script**:
    - Ouvrez le fichier `trae_proxy.py`.
    - **Modifiez `TARGET_API_BASE_URL`** : Remplacez-la par l'URL de base de l'API au format OpenAI du site auquel vous souhaitez réellement vous connecter (par exemple : `"https://your-api.example.com"`).
    - **Vérifiez les chemins des certificats** : Le script lit par défaut `api.openai.com.crt` et `api.openai.com.key` depuis `mtga\ca`. Si vos certificats ne se trouvent pas à cet emplacement, modifiez les valeurs de `CERT_FILE` et `KEY_FILE`, ou copiez ces deux fichiers dans le `CERT_DIR` spécifié par le script.

**Exécuter le serveur proxy :**

Ouvrez l'invite de commandes (cmd) ou PowerShell **en tant qu'administrateur** (car il faut écouter sur le port 443), puis exécutez :

```bash
python trae_proxy.py
```

Si tout se passe bien, vous devriez voir les journaux de démarrage du serveur.

##### Étape 5 : Configurer Trae IDE

1.  Ouvrez et connectez-vous à Trae IDE.
2.  Dans la boîte de dialogue IA, cliquez sur l'icône du modèle en bas à droite et sélectionnez "Ajouter un modèle" à la fin.
3.  **Fournisseur** : Sélectionnez `OpenAI`.
4.  **Modèle** : Sélectionnez "Modèle personnalisé".
5.  **ID du modèle** : Saisissez la valeur que vous avez définie pour `CUSTOM_MODEL_ID` dans le script Python (par exemple : `my-custom-local-model`).
6.  **Clé API** :
    - Si votre API cible nécessite une clé API et que Trae la transmet via `Authorization: Bearer <key>`, alors la clé saisie ici sera transmise par le proxy Python.
    - Lors de la configuration d'OpenAI dans Trae, la clé API est liée à la configuration `remove_reasoning_content`. Notre proxy Python ne gère pas cette logique, il se contente de transmettre l'en-tête Authorization. Vous pouvez essayer de saisir la clé requise par votre API cible, ou une clé arbitraire au format `sk-xxxx`.

7.  Cliquez sur "Ajouter un modèle".
8.  Revenez à la boîte de chat IA et sélectionnez le modèle personnalisé que vous venez d'ajouter dans le menu en bas à droite.

Maintenant, lorsque vous interagissez avec ce modèle personnalisé via Trae, les requêtes devraient passer par votre proxy Python local et être redirigées vers l'`TARGET_API_BASE_URL` que vous avez configuré.

**Conseils de dépannage :**

- **Conflit de port** : Si le port 443 est déjà occupé (par exemple par IIS, Skype ou un autre service), le script Python échouera à démarrer. Vous devez arrêter le service qui utilise ce port, ou modifier le script Python et Nginx (si utilisé) pour écouter sur un autre port (mais cela est plus complexe, car Trae accède en dur au port 443 de `https://api.openai.com`).
- **Pare-feu** : Assurez-vous que le pare-feu Windows autorise les connexions entrantes sur le port 443 pour Python (même s'il s'agit d'une connexion locale `127.0.0.1`, une configuration spéciale du pare-feu n'est généralement pas nécessaire, mais cela vaut la peine de vérifier).
- **Problèmes de certificat** : Si Trae signale une erreur liée à SSL/TLS, vérifiez attentivement que le certificat d'autorité de certification (CA) est correctement installé dans les "Autorités de certification racines de confiance", et que le proxy Python charge correctement les fichiers `api.openai.com.crt` et `.key`.
- **Journaux du proxy** : Le script Python imprime quelques journaux qui peuvent vous aider à diagnostiquer les problèmes.

Cette solution est plus intégrée que l'utilisation directe de vproxy + nginx, car elle place la terminaison TLS et la logique de proxy dans un seul script Python, ce qui la rend plus adaptée à la validation rapide de prototypes sur Windows.

#### macOS

-> [Méthode de démarrage par script pour Mac OS](README_macOS_cli.md)

---

## 😎 Restez à jour

Cliquez sur les boutons Star et Watch en haut à droite du dépôt pour obtenir les dernières mises à jour.

![star to keep latest](https://github.com/xiaoliuzhuan/model-relay-desktop/blob/main/images/star-to-keep-latest.gif?raw=true)

---

## Références

Le répertoire `ca` est référencé depuis le dépôt `wkgcass/vproxy`, merci au grand maître !
