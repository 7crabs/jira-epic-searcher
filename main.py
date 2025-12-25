#!/usr/bin/env python3
"""
Jiraエピック一覧取得スクリプト

使用方法:
    python main.py <email> <api_token> <space_name> [jira_domain]

引数:
    email: Jiraアカウントのメールアドレス
    api_token: Jira APIトークン
    space_name: プロジェクトキー（スペース名）
    jira_domain: Jiraのドメイン（オプション、例: your-domain.atlassian.net）
                指定しない場合、emailから推測します
"""

import sys
import base64
import json
import argparse
from typing import Optional
import requests


def extract_domain_from_email(email: str) -> str:
    """メールアドレスからJiraドメインを推測"""
    # メールアドレスのドメイン部分を取得
    # 例: user@company.com -> company.atlassian.net
    domain_part = email.split('@')[1].split('.')[0]
    return f"{domain_part}.atlassian.net"


def get_jira_base_url(jira_domain: Optional[str], email: str) -> str:
    """JiraのベースURLを取得"""
    if jira_domain:
        domain = jira_domain
    else:
        domain = extract_domain_from_email(email)
    
    if not domain.startswith('http'):
        domain = f"https://{domain}"
    
    return domain.rstrip('/')


def create_basic_auth_header(email: str, api_token: str) -> str:
    """Basic認証ヘッダーを作成"""
    credentials = f"{email}:{api_token}"
    encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded}"


def search_epics(jira_url: str, auth_header: str, project_key: str, max_results: int = 100, debug: bool = False) -> dict:
    """
    Jira APIを使用してエピック一覧を取得
    
    Args:
        jira_url: JiraのベースURL
        auth_header: Basic認証ヘッダー
        project_key: プロジェクトキー
        max_results: 最大取得件数
    
    Returns:
        APIレスポンスのJSONデータ
    """
    # 新しいエンドポイント: /rest/api/3/search/jql
    search_url = f"{jira_url}/rest/api/3/search/jql"
    
    # JQLクエリ: 指定されたプロジェクトのエピックを検索
    # 複数のパターンを試す（日本語名「エピック」と英語名「Epic」の両方を試す）
    epic_type_names = ["エピック", "Epic"]  # 日本語を優先
    
    headers = {
        "Authorization": auth_header,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # フィールド定義
    fields_list = [
        "summary",
        "status",
        "description",
        "created",
        "updated",
        "assignee",
        "reporter",
        "issuetype"  # issue typeも取得して確認
    ]
    
    if debug:
        print(f"デバッグ: リクエストURL = {search_url}")
    
    # 各エピックタイプ名を順番に試す
    for epic_type_name in epic_type_names:
        jql = f'project = "{project_key}" AND issuetype = "{epic_type_name}"'
        
        if debug:
            print(f"\nデバッグ: JQLクエリ = {jql}")
        
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": fields_list
        }
        
        try:
            if debug:
                print(f"デバッグ: リクエストペイロード = {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            response = requests.post(search_url, headers=headers, json=payload)
            
            if debug:
                print(f"デバッグ: レスポンスステータス = {response.status_code}")
                try:
                    response_json = response.json()
                    print(f"デバッグ: レスポンスボディ = {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                except:
                    print(f"デバッグ: レスポンステキスト = {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            # 結果が0件でない場合、または最後の試行の場合は結果を返す
            issues = result.get("issues", [])
            if len(issues) > 0:
                if debug:
                    print(f"デバッグ: '{epic_type_name}' で {len(issues)} 件見つかりました！")
                return result
            elif debug:
                print(f"デバッグ: '{epic_type_name}' で検索結果が0件でした。")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                # JQLエラーの場合、次のパターンを試す
                if debug:
                    error_detail = e.response.text
                    print(f"デバッグ: '{epic_type_name}' でJQLエラー: {error_detail}")
                continue
            else:
                # その他のHTTPエラーは再発生
                raise
        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどは再発生
            raise
    
    # すべてのパターンで0件の場合、代替検索方法を試す
    if debug:
        print("\nデバッグ: すべての標準パターンで検索結果が0件でした。")
        print("デバッグ: 代替検索方法を試します...")
        
        # プロジェクトのすべてのissue typeを取得
        try:
            issue_types_url = f"{jira_url}/rest/api/3/issuetype"
            issue_types_response = requests.get(issue_types_url, headers=headers)
            if issue_types_response.status_code == 200:
                all_issue_types = issue_types_response.json()
                epic_types = [it for it in all_issue_types if 'epic' in it.get('name', '').lower() or it.get('hierarchyLevel', 0) == 1]
                if epic_types:
                    print(f"デバッグ: 見つかったエピックタイプ: {[it.get('name') for it in epic_types]}")
                    # 最初のエピックタイプで再検索
                    if epic_types:
                        epic_name = epic_types[0].get('name')
                        alt_jql = f'project = "{project_key}" AND issuetype = "{epic_name}"'
                        print(f"デバッグ: 代替JQLクエリ = {alt_jql}")
                        alt_payload = {
                            "jql": alt_jql,
                            "maxResults": max_results,
                            "fields": fields_list
                        }
                        alt_response = requests.post(search_url, headers=headers, json=alt_payload)
                        if alt_response.status_code == 200:
                            alt_result = alt_response.json()
                            alt_issues = alt_result.get("issues", [])
                            if len(alt_issues) > 0:
                                print(f"デバッグ: 代替検索で {len(alt_issues)} 件見つかりました！")
                                return alt_result
        except Exception as e:
            if debug:
                print(f"デバッグ: 代替検索中にエラー: {str(e)}")
    
    # すべて失敗した場合は空の結果を返す
    return {"issues": [], "isLast": True, "nextPageToken": None}


def display_epics(search_results: dict):
    """エピック一覧を表示"""
    issues = search_results.get("issues", [])
    is_last = search_results.get("isLast", True)
    next_page_token = search_results.get("nextPageToken")
    
    issue_count = len(issues)
    if not is_last and next_page_token:
        print(f"\nエピック一覧 (表示: {issue_count}件、続きあり)\n")
    else:
        print(f"\nエピック一覧 (合計: {issue_count}件)\n")
    print("=" * 80)
    
    if not issues:
        print("エピックが見つかりませんでした。")
        return
    
    for idx, issue in enumerate(issues, 1):
        key = issue.get("key", "N/A")
        fields = issue.get("fields", {})
        summary = fields.get("summary", "N/A")
        status = fields.get("status", {})
        status_name = status.get("name", "N/A") if status else "N/A"
        
        assignee = fields.get("assignee")
        assignee_name = assignee.get("displayName", "未割り当て") if assignee else "未割り当て"
        
        reporter = fields.get("reporter")
        reporter_name = reporter.get("displayName", "N/A") if reporter else "N/A"
        
        created = fields.get("created", "N/A")
        updated = fields.get("updated", "N/A")
        
        print(f"\n[{idx}] {key}: {summary}")
        print(f"    ステータス: {status_name}")
        print(f"    担当者: {assignee_name}")
        print(f"    報告者: {reporter_name}")
        print(f"    作成日: {created}")
        print(f"    更新日: {updated}")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Jiraのエピック一覧を取得します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("email", help="Jiraアカウントのメールアドレス")
    parser.add_argument("api_token", help="Jira APIトークン")
    parser.add_argument("space_name", help="プロジェクトキー（スペース名）")
    parser.add_argument(
        "jira_domain",
        nargs="?",
        default=None,
        help="Jiraのドメイン（オプション、例: your-domain.atlassian.net）"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="最大取得件数（デフォルト: 100）"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="デバッグモード（リクエストとレスポンスを表示）"
    )
    
    args = parser.parse_args()
    
    try:
        # Jira URLを構築
        jira_url = get_jira_base_url(args.jira_domain, args.email)
        print(f"Jira URL: {jira_url}")
        print(f"プロジェクトキー: {args.space_name}")
        
        # 認証ヘッダーを作成
        auth_header = create_basic_auth_header(args.email, args.api_token)
        
        # エピックを検索
        print("\nエピックを検索中...")
        search_results = search_epics(jira_url, auth_header, args.space_name, args.max_results, args.debug)
        
        # 結果を表示
        display_epics(search_results)
        
        # デバッグモードの場合、プロジェクトのissue typeも確認
        if args.debug:
            print("\n" + "=" * 80)
            print("デバッグ: プロジェクトのすべてのissue typeを確認中...")
            try:
                # プロジェクト情報を取得してissue typeを確認
                project_url = f"{jira_url}/rest/api/3/project/{args.space_name}"
                project_headers = {
                    "Authorization": auth_header,
                    "Accept": "application/json"
                }
                project_response = requests.get(project_url, headers=project_headers)
                if project_response.status_code == 200:
                    project_data = project_response.json()
                    print(f"プロジェクト名: {project_data.get('name', 'N/A')}")
                    print(f"プロジェクトキー: {project_data.get('key', 'N/A')}")
                    
                    # issue typesを取得
                    issue_types_url = f"{jira_url}/rest/api/3/project/{args.space_name}/statuses"
                    issue_types_response = requests.get(issue_types_url, headers=project_headers)
                    if issue_types_response.status_code == 200:
                        print("\n利用可能なIssue Types:")
                        # 別のエンドポイントでissue typesを取得
                        issue_types_url2 = f"{jira_url}/rest/api/3/issuetype"
                        issue_types_response2 = requests.get(issue_types_url2, headers=project_headers)
                        if issue_types_response2.status_code == 200:
                            issue_types = issue_types_response2.json()
                            for it in issue_types:
                                print(f"  - {it.get('name', 'N/A')} (id: {it.get('id', 'N/A')})")
            except Exception as e:
                print(f"デバッグ情報の取得中にエラー: {str(e)}")
        
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
