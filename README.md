# Jira エピック一覧取得ツール

Jira APIを使用して、指定したプロジェクトのエピック一覧を取得するPythonスクリプトです。

## 機能

- 指定したプロジェクトのエピック一覧を取得
- 日本語（「エピック」）と英語（「Epic」）の両方のissue type名に対応
- エピックの詳細情報（キー、サマリー、ステータス、担当者、報告者、作成日、更新日）を表示
- デバッグモードで詳細な情報を表示可能

## 必要な環境

- Python 3.9以上
- [uv](https://github.com/astral-sh/uv) (Pythonパッケージマネージャー)
- requests ライブラリ（uv syncで自動インストールされます）

## インストール

1. リポジトリをクローンまたはダウンロードします

2. [uv](https://github.com/astral-sh/uv)をインストールします（まだインストールしていない場合）：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. 依存関係をインストールします：

```bash
uv sync
```

これにより、`pyproject.toml`に定義された依存関係（`requests`など）が自動的にインストールされます。

### スクリプトの実行

依存関係をインストール後、以下のいずれかの方法でスクリプトを実行できます：

```bash
# uv runを使用（推奨）
uv run python main.py <email> <api_token> <space_name> [jira_domain]

# または、uv syncで作成された仮想環境を有効化してから実行
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows
python main.py <email> <api_token> <space_name> [jira_domain]
```

## Jira APIトークンの発行方法

このスクリプトを使用するには、Jira APIトークンが必要です。以下の手順でAPIトークンを発行してください。

### 1. Atlassianアカウントにログイン

[AtlassianアカウントのAPIトークン管理ページ](https://id.atlassian.com/manage-profile/security/api-tokens)にログインします。

### 2. APIトークンを作成

1. 「**API トークンを作成**」を選択します
2. APIトークンには、その機能を説明する名前を付けます（例：「エピック一覧取得スクリプト」）
3. APIトークンの**有効期限**を選択します（1日〜365日、デフォルトは1年）
4. 「**作成**」を選択します
5. 「**クリップボードにコピー**」を選択して、トークンを安全な場所に保存します

**重要**: この手順が完了すると、APIトークンを復元できなくなります。APIトークンをパスワードマネージャーに保存することをお勧めします。

### 3. APIトークンのスコープ（オプション）

APIトークンを作成する際に、スコープを選択できます。スコープによって、APIトークンが実行できる権限を制限できます。より安全であるため、スコープ付きのAPIトークンを作成することをお勧めします。

- **Jira クラシック スコープ**: Jiraアプリ内のデータへのアクセス
- **Confluence クラシック スコープ**: Confluenceアプリ内のデータへのアクセス

このスクリプトでは、Jiraのデータを読み取る権限が必要です。

### 参考リンク

詳細については、[Atlassian公式ドキュメント](https://support.atlassian.com/ja/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)を参照してください。

## 使用方法

### 基本的な使用方法

```bash
uv run python main.py <email> <api_token> <space_name> [jira_domain]
```

または、仮想環境を有効化している場合：

```bash
python main.py <email> <api_token> <space_name> [jira_domain]
```

### 引数の説明

- `email`: Jiraアカウントのメールアドレス
- `api_token`: Jira APIトークン（上記の手順で発行したトークン）
- `space_name`: プロジェクトキー（スペース名、例：`CDP`）
- `jira_domain`: Jiraのドメイン（オプション、例：`geniee.atlassian.net`）
  - 指定しない場合、emailから自動的に推測します

### 使用例

#### 例1: ドメインを自動推測する場合

```bash
uv run python main.py user@example.com YOUR_API_TOKEN CDP
```

この場合、`user@example.com`から`example.atlassian.net`を推測します。

#### 例2: ドメインを明示的に指定する場合

```bash
uv run python main.py user@example.com YOUR_API_TOKEN CDP geniee.atlassian.net
```

#### 例3: 最大取得件数を指定する場合

```bash
uv run python main.py user@example.com YOUR_API_TOKEN CDP geniee.atlassian.net --max-results 200
```

#### 例4: デバッグモードで実行する場合

```bash
uv run python main.py user@example.com YOUR_API_TOKEN CDP geniee.atlassian.net --debug
```

**注**: 仮想環境を有効化している場合は、`uv run`を省略して`python main.py`を直接実行することもできます。

デバッグモードでは、以下の情報が表示されます：
- リクエストURL
- JQLクエリ
- リクエストペイロード
- レスポンスステータス
- レスポンスボディ
- 利用可能なissue type一覧

### オプション

- `--max-results <数値>`: 最大取得件数を指定（デフォルト: 100）
- `--debug`: デバッグモードを有効化（リクエストとレスポンスの詳細を表示）

## 出力例

```
Jira URL: https://geniee.atlassian.net
プロジェクトキー: CDP

エピックを検索中...

エピック一覧 (合計: 5件)

================================================================================

[1] CDP-19: 【完了】初期開発環境整備
    ステータス: 完了
    担当者: 田中太郎
    報告者: 佐藤花子
    作成日: 2024-01-15T10:30:00.000+0000
    更新日: 2024-02-20T15:45:00.000+0000
--------------------------------------------------------------------------------

[2] CDP-31: 【完了】ワークフローエンジン・初期コア設計
    ステータス: 完了
    担当者: 未割り当て
    報告者: 佐藤花子
    作成日: 2024-01-20T09:00:00.000+0000
    更新日: 2024-03-10T14:20:00.000+0000
--------------------------------------------------------------------------------
...
```

## トラブルシューティング

### エラー: 認証に失敗しました

- APIトークンが正しいか確認してください
- APIトークンの有効期限が切れていないか確認してください
- メールアドレスが正しいか確認してください

### エラー: JQLクエリが無効です

- プロジェクトキーが正しいか確認してください
- Jiraのプロジェクトにアクセス権限があるか確認してください

### エピックが見つかりません

- プロジェクトキーが正しいか確認してください
- プロジェクトにエピックが存在するか確認してください
- エピックへのアクセス権限があるか確認してください
- デバッグモード（`--debug`）で実行して、詳細な情報を確認してください

### エラー: APIリクエストエラー: 410

このエラーは、古いAPIエンドポイントが使用されている場合に発生します。スクリプトは最新のAPIエンドポイント（`/rest/api/3/search/jql`）を使用しているため、このエラーが発生する場合は、スクリプトを最新版に更新してください。

## 技術的な詳細

### 使用しているAPI

- **エンドポイント**: `/rest/api/3/search/jql` (POST)
- **認証方式**: Basic認証（メールアドレス + APIトークン）
- **JQLクエリ**: `project = "<プロジェクトキー>" AND issuetype = "エピック"` または `project = "<プロジェクトキー>" AND issuetype = "Epic"`

### Issue Type名の自動検出

スクリプトは以下の順序でエピックを検索します：

1. 日本語の「エピック」で検索
2. 英語の「Epic」で検索
3. デバッグモードの場合、利用可能なすべてのissue typeからエピックタイプを自動検出して再検索

## ライセンス

このプロジェクトのライセンス情報は、プロジェクトのルートディレクトリにあるLICENSEファイルを参照してください。

## 参考リンク

- [Atlassian APIトークン管理ドキュメント](https://support.atlassian.com/ja/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [Jira REST API ドキュメント](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [JQL (Jira Query Language) リファレンス](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

