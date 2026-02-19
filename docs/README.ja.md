# MTGA

<picture>
    <img alt="MTGA" src="https://github.com/BiFangKNT/mtga/blob/gui/icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](../README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](README.fr.md) [![Documentação em Português (Brasil)](https://img.shields.io/badge/docs-Português-purple)](README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](README.ru.md)

## 概要

MTGA は、Windows と macOS 向けのローカルプロキシベースの IDE 固定モデルプロバイダーソリューションです。

**注意：本プロジェクトは現在、openai 形式の API のみをサポートしています。他の形式は openai 形式に変換してからご利用ください。**

<details>
  <summary>何も見えないよ~~</summary>
  <br>
  <p>MTGA は Make T Great Again の略です！</p>
 </details>

## 目次

- [MTGA](#mtga)
  - [概要](#概要)
  - [目次](#目次)
  - [更新履歴](#更新履歴)
    - [v1.2.0 (最新)](#v120-最新)
    - [v1.1.1](#v111)
    - [v1.1.0](#v110)
    - [v1.0.0](#v100)
  - [クイックスタート](#クイックスタート)
    - [Windows ユーザー（GUIワンクリック起動方式）](#windows-ユーザーguiワンクリック起動方式)
    - [macOS ユーザー（アプリケーションインストール）](#macos-ユーザーアプリケーションインストール)
      - [インストール方法](#インストール方法)
      - [使用方法](#使用方法)
  - [macOSで「パッケージが壊れています」問題を解決する方法](#macosでパッケージが壊れています問題を解決する方法)
    - [グラフィカルな解決方法](#グラフィカルな解決方法)
    - [コマンドラインでの解決方法](#コマンドラインでの解決方法)
  - [スクリプトからの起動](#スクリプトからの起動)
    - [ステップ 0：環境準備](#ステップ-0環境準備)
      - [Windows](#windows)
        - [ステップ 1：自己署名証明書の生成](#ステップ-1自己署名証明書の生成)
        - [ステップ 2：WindowsにCA証明書を信頼させる](#ステップ-2windowsにca証明書を信頼させる)
        - [ステップ 3：Hostsファイルの修正](#ステップ-3hostsファイルの修正)
        - [ステップ 4：ローカルプロキシサーバーを実行する (Python)](#ステップ-4ローカルプロキシサーバーを実行する-python)
        - [ステップ 5：Trae IDE を設定する](#ステップ-5trae-ide-を設定する)
      - [macOS](#macos)
  - [😎 最新情報の取得](#-最新情報の取得)
  - [クレジット](#クレジット)

---

## 更新履歴

### v1.2.0 (最新)

- 🔄 **モデルマッピングアーキテクチャのリファクタリング** - 「1対1マッピング」から「統一マッピングモデル」アーキテクチャへ変更
  - trae側は統一されたマッピングモデルIDを使用し、MTGAは設定グループで実際のバックエンドモデルを切り替え
  - プロキシサーバーはモデルIDマッピングとMTGA認証検証をサポート
  - グローバル設定でマッピングモデルIDとMTGA認証Keyの設定をサポート
- ⚡ **設定グループ管理の最適化** - 設定グループのフィールドと検証ロジックをリファクタリング
  - 設定グループ名は任意に、API URL、実際のモデルID、API Keyを必須に変更
  - 目的モデルIDフィールドを削除し、グローバルマッピング設定に変更
  - 設定グループのテーブルヘッダーをリネームし、旧設定ファイルとの下位互換を維持
- 🧪 **自動テスト機能の追加** - 完全なモデル接続テスト体制
  - 設定保存後にモデル接続を自動テスト (GET `/v1/models/{モデルid}`)
  - 手動ヘルスチェック機能、チャット補完テストをサポート (POST `/v1/chat/completions`)
  - レスポンス内容やトークン消費統計を含む詳細なテストログ出力
- 🎯 **ユーザーエクスペリエンスの強化** - ヘルスチェックボタンと詳細なヒントを追加
  - ヘルスチェックボタンはツールチップによるトークン消費リスク説明をサポート
  - 非同期テストでUIブロックを回避し、充実したエラーハンドリング機構
  - API Keyの安全表示（マスク処理）

<details>
<summary>過去のバージョン</summary>

### v1.1.1

- 🐛 **hosts 修正機能の問題を修正** - hosts ファイル修正時の改行コード異常の問題を解決

### v1.1.0

- ✨ **ユーザーデータ管理機能を追加** - 単一ファイル版でユーザーデータの永続的保存をサポート
  - データ保存場所：Windows `%APPDATA%\MTGA\`、macOS/Linux `~/.mtga/`
  - バックアップ、復元、ユーザーデータ削除をサポート
  - 設定ファイル、SSL証明書、hostsバックアップの自動永続化
- 🔧 **単一ファイルビルドの最適化** - `build_onefile.bat` を改良し、バージョン番号の変数化をサポート
- 🎯 **ユーザーインターフェースの改善** - 設定グループリストの更新ボタンを追加、インターフェースレイアウトを最適化
- 📖 **ドキュメントの充実** - 単一ファイルビルドガイドを新規追加、プロジェクトドキュメントを更新

### v1.0.0

- ✅ **Mac OS 対応** - macOS アプリケーションインストール方式をサポート
- 🔄 **デフォルトプロバイダ変更** - DeepSeek から OpenAI へ変更
- 📦 **ファイルリファクタリング** - ds 関連ファイルを `*_ds.*` 形式でリネームしてアーカイブ
- 🌐 **API URL 形式変更** - `https://your-api.example.com/v1` から `https://your-api.example.com` へ変更

</details>

---

## クイックスタート

### Windows ユーザー（GUIワンクリック起動方式）

1. [GitHub Releases](https://github.com/BiFangKNT/mtga/releases) から最新バージョンの `MTGA_GUI-v{バージョン番号}-x64.exe` をダウンロード
2. ダウンロードした exe ファイルをダブルクリックで実行（管理者権限が必要）
3. 開いたグラフィカルインターフェースで、API URL とモデル ID を入力
   - **API URL はドメインのみ入力（ポート番号は任意、分からない場合は入力不要）、後続のルーティングは不要です。例：`https://your-api.example.com`**
   - **マルチモーダル機能を有効にしたい場合、モデル名を内蔵マルチモーダルモデル名にマッピングできます：**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
4. 「ワンクリックですべてのサービスを起動」ボタンをクリック
5. プログラムが自動的に以下の操作を完了するのを待機：
   - 証明書の生成とインストール
   - hostsファイルの変更
   - プロキシサーバーの起動
6. 完了後、[第 5 步：配置 Trae IDE](#第-5-步配置-trae-ide) に従ってIDE設定を実施

> [!NOTE]
>
> - 初回実行時はファイアウォールのアクセス許可が必要な場合があります
> - 単一ファイル版はユーザーデータの永続的保存をサポートし、設定と証明書は自動的に保存されます

### macOS ユーザー（アプリケーションインストール）

#### インストール方法

1. [GitHub Releases](https://github.com/BiFangKNT/mtga/releases) から最新バージョンの `MTGA_GUI-v{バージョン番号}-aarch64.dmg` をダウンロード
2. DMG ファイルをダブルクリックし、システムが自動的にインストールパッケージをマウント
3. `MTGA_GUI.app` を `Applications` フォルダにドラッグ＆ドロップ
4. ランチャーまたは Applications フォルダからアプリケーションを起動

#### 使用方法

1. `MTGA_GUI.app`を起動（初回実行時はシステム環境設定で実行を許可する必要がある場合があります）
2. グラフィカルインターフェースで以下を入力：
   - **API URL**：あなたのAPIサービスアドレス（例：`https://your-api.example.com`）
   - **マルチモーダル機能を有効にしたい場合、モデル名を内蔵マルチモーダルモデル名にマッピングできます：**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
3. 「一键启动全部服务」ボタンをクリック
4. プログラムが自動的に完了します：
   - SSL証明書を生成し、システムキーチェーンにインストール
   - `/etc/hosts`ファイルを修正（管理者権限が必要）
5. 開かれたキーチェーンウィンドウで生成された証明書を手動で信頼設定、デフォルト名は`MTGA_CA`
6. ローカルプロキシサーバーを起動
7. 下記の[Trae IDE 設定](#第-5-步配置-trae-ide)に従って設定を完了

> [!NOTE]
>
> - 証明書のインストールと hosts の変更には管理者権限が必要です
> - 「パッケージが壊れています」というメッセージが表示された場合は、[macOSで「パッケージが壊れています」問題を解決する方法](#macosでパッケージが壊れています問題を解決する方法) を参照してください

## macOSで「パッケージが壊れています」問題を解決する方法

`MTGA_GUI.app` を起動した際に以下のような警告が表示された場合：

<img width="244" height="223" alt="app corrupted" src="../images/app-corrupted.png?raw=true" />

**キャンセルをクリック**してください。その後、以下の手順に従って問題を解決してください。

### グラフィカルな解決方法

1. [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest) から `Sentinel.dmg` をダウンロードします。
2. `Sentinel.dmg` ファイルをダブルクリックし、`Sentinel.app` を `Applications` フォルダにドラッグ＆ドロップします。
3. Launchpad または Applications フォルダから `Sentinel.app` を起動します。
4. 本プロジェクトの `MTGA_GUI.app` を `Sentinel.app` の左側のウィンドウにドラッグ＆ドロップします。
   - <img width="355.33" height="373.33" alt="sentinel add app" src="../images/sentinel-add-app.png?raw=true" />

これにより `MTGA_GUI.app` は自動的に処理され、起動します。

### コマンドラインでの解決方法

1. `MTGA_GUI.app` のフルパスを確認します（例：`/Applications/MTGA_GUI.app`）。
2. ターミナル（Terminal）を開きます。
3. 以下のコマンドを実行して `MTGA_GUI.app` の署名を解除します：
   ```zsh
   xattr -d com.apple.quarantine <アプリのフルパス>
   ```
   これにより `MTGA_GUI.app` の `com.apple.quarantine` 拡張属性が削除されます。
4. `MTGA_GUI.app` を起動します。

---

## スクリプトからの起動

### ステップ 0：環境準備

#### Windows

- Windows 10以上
- 管理者権限を所持
- Python環境をインストール、推奨はPython 3.10以上
- Gitをインストール

##### ステップ 1：自己署名証明書の生成

Git Bashを開く：

```bash
# ca ディレクトリに移動
cd "mtga/ca"

# 1. CA証明書の生成 (ca.crt と ca.key)
./genca.sh
```

`./genca.sh`を実行すると、"Do you want to generate ca cert and key? [yes/no]"と聞かれるので、`y`を入力してEnter。その後、いくつかの情報入力が要求されます：

- `Country Name (2 letter code) []`: `CN`と入力（または他の国コード）
- 他のフィールド（State, Locality, Organization, Common Name for CAなど）は必要に応じて入力または空欄、`X`と入力することを推奨。Common Nameは`MTGA_CA`などと入力可能。メールは空欄可。

```bash
# 2. api.openai.com のサーバー証明書の生成 (api.openai.com.crt と api.openai.com.key)
# このスクリプトは同ディレクトリ下の api.openai.com.subj と api.openai.com.cnf 設定ファイルを使用
./gencrt.sh api.openai.com
```

実行完了後、`mtga\ca`ディレクトリに以下の重要ファイルが生成されます：

- `ca.crt`（カスタムCA証明書）
- `ca.key`（カスタムCA秘密鍵 - **絶対に漏洩しないでください**）
- `api.openai.com.crt`（ローカルプロキシサーバー用SSL証明書）
- `api.openai.com.key`（ローカルプロキシサーバー用SSL秘密鍵 - **絶対に漏洩しないでください**）

##### ステップ 2：WindowsにCA証明書を信頼させる

1.  `mtga\ca\ca.crt`ファイルを探す
2.  `ca.crt`ファイルをダブルクリックし、証明書ビューアを開く
3.  「証明書のインストール...」ボタンをクリック
4.  「現在のユーザー」または「ローカルコンピューター」を選択。「ローカルコンピューター」を推奨（管理者権限が必要）、これにより全ユーザーに適用
5.  次のダイアログで「すべての証明書を次のストアに配置する」を選択し、「参照...」をクリック
6.  「信頼されたルート証明機関」を選択し、「OK」をクリック
7.  「次へ」をクリックし、「完了」。セキュリティ警告が表示された場合は「はい」を選択

##### ステップ 3：Hostsファイルの修正

**⚠️警告：この手順を実行すると、元の OpenAI の API にアクセスできなくなります。Web サイトの使用には影響しません。**

管理者権限で Hosts ファイルを編集し、`api.openai.com` をローカルマシンに向ける必要があります。

1.  Hosts ファイルのパス: `C:\Windows\System32\drivers\etc\hosts`
2.  管理者としてメモ帳（または他のテキストエディタ）を使用してこのファイルを開きます。
3.  ファイルの末尾に次の行を追加します：
    ```
    127.0.0.1 api.openai.com
    ```
4.  ファイルを保存します。

##### ステップ 4：ローカルプロキシサーバーを実行する (Python)

**プロキシサーバーを実行する前に：**

1.  **依存関係をインストール**:
    ```bash
    pip install Flask requests
    ```
2.  **スクリプトを設定**:
    - `trae_proxy.py` ファイルを開きます。
    - **`TARGET_API_BASE_URL` を変更**: これを、実際に接続したいサイトの OpenAI 形式 API のベース URL (例: `"https://your-api.example.com"`) に置き換えます。
    - **証明書パスを確認**: スクリプトはデフォルトで `mtga\ca` から `api.openai.com.crt` と `api.openai.com.key` を読み取ります。証明書がこのパスにない場合は、`CERT_FILE` と `KEY_FILE` の値を変更するか、これら 2 つのファイルをスクリプトが指定する `CERT_DIR` にコピーしてください。

**プロキシサーバーを実行：**

コマンドプロンプト (cmd) または PowerShell を**管理者として実行**で開き（ポート 443 をリッスンするため）、次を実行します：

```bash
python trae_proxy.py
```

すべてが順調に進めば、サーバー起動のログが表示されるはずです。

##### ステップ 5：Trae IDE を設定する

1.  Trae IDE を開いてログインします。
2.  AI ダイアログで、右下隅のモデルアイコンをクリックし、末尾の「モデルを追加」を選択します。
3.  **プロバイダー**：`OpenAI` を選択します。
4.  **モデル**：「カスタムモデル」を選択します。
5.  **モデル ID**：Python スクリプトで `CUSTOM_MODEL_ID` に定義した値 (例: `my-custom-local-model`) を入力します。
6.  **API キー**：
    - ターゲット API が API キーを必要とし、Trae がそれを `Authorization: Bearer <key>` で渡す場合、ここで入力したキーは Python プロキシによって転送されます。
    - Trae で OpenAI を設定する場合、API キーは `remove_reasoning_content` 設定に関連します。私たちの Python プロキシはこのロジックを処理せず、Authorization ヘッダーを単純に転送するだけです。ターゲット API に必要なキー、または任意の `sk-xxxx` 形式のキーを入力してみることができます。

7.  「モデルを追加」をクリックします。
8.  AI チャットボックスに戻り、右下隅で先ほど追加したカスタムモデルを選択します。

これで、Trae を通じてこのカスタムモデルと対話するとき、リクエストはローカルの Python プロキシを経由し、設定した `TARGET_API_BASE_URL` に転送されるはずです。

**トラブルシューティングのヒント：**

- **ポート競合**：ポート443が既に使用されている場合（例：IIS、Skype、その他のサービス）、Pythonスクリプトの起動に失敗します。該当ポートを使用しているサービスを停止するか、PythonスクリプトおよびNginx（使用している場合）のリスンポートを変更する必要があります（ただし、Traeが`https://api.openai.com`へのアクセスをポート443にハードコードしているため、より複雑になります）。
- **ファイアウォール**：WindowsファイアウォールがPythonによるポート443へのインバウンド接続を許可していることを確認してください（ローカル接続`127.0.0.1`であり、通常は特別なファイアウォール設定は不要ですが、確認する価値はあります）。
- **証明書の問題**：TraeがSSL/TLS関連のエラーを報告する場合は、CA証明書が「信頼されたルート証明機関」に正しくインストールされているか、およびPythonプロキシが`api.openai.com.crt`と`.key`を正しく読み込んでいるかを注意深く確認してください。
- **プロキシログ**：Pythonスクリプトはいくつかのログを出力します。これは問題の診断に役立ちます。

このソリューションは、vproxy + nginxを直接使用する方法よりも統合度が高く、TLS終端とプロキシロジックの両方を1つのPythonスクリプトにまとめているため、Windows上でのプロトタイプ検証に適しています。

#### macOS

-> [Mac OS スクリプト起動方法](https://github.com/BiFangKNT/mtga/blob/gui/docs/README_macOS_cli.md)

---

## 😎 最新情報の取得

リポジトリ右上の Star と Watch ボタンをクリックして、最新の動向を取得してください。

![star to keep latest](https://github.com/BiFangKNT/mtga/blob/gui/images/star-to-keep-latest.gif?raw=true)

---

## クレジット

`ca`ディレクトリは`wkgcass/vproxy`リポジトリから引用しています。感謝します！
