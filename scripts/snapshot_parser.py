"""自动化抓取 GKD 快照节点并生成规则草稿

使用方法（需先安装依赖）：
    pip install playwright
    playwright install chromium

然后：
    python3 scripts/snapshot_parser.py https://i.gkd.li/i/12345678

输出会在控制台打印 JSON 草稿，可重定向到文件。

原理：
1. Playwright 启动无头浏览器访问快照链接。
2. 监听到前端向 detect.gkd.li 发起的接口请求并获取快照数据。
3. 从节点列表中提取 vid/text/className/xpath 等属性。
4. 按照 GKD 规则结构拼装草稿。

最后部分还演示了如何把结果交给 AI 进一步润色。

注意：如果快照链接已过期，返回的数据可能为空。

"""
import sys
import json
import re
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


def fetch_snapshot_data(url: str, timeout: int = 10000) -> dict | None:
    """用无头浏览器加载页面并拦截数据接口。

    返回的字典与前端响应一致, 通常包含 `nodes` 列表。
    """
    result = None

    def _on_response(response):
        nonlocal result
        # 监控 detectSnapshot 和 getImportId 两类 API
        u = response.url
        if "detectSnapshot" in u or "getImportId" in u:
            try:
                payload = response.json()
            except Exception:
                return
            # 检测到实际快照数据
            if isinstance(payload, dict) and payload.get("nodes"):
                result = payload

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("response", _on_response)
        page.goto(url, timeout=timeout)
        # 等待页面加载完成
        page.wait_for_timeout(2000)
        browser.close()
    return result


def nodes_to_rule(nodes: list[dict]) -> dict:
    """把节点列表转成一个简单的 GKD 规则草稿结构。"""
    # 最简单的示例, 只使用 xpath
    matches = []
    for n in nodes:
        xpath = n.get("xpath") or n.get("xpathWithClass") or n.get("path")
        if xpath:
            matches.append(xpath)
    rule = {
        "name": "[ChangeMe] 规则名称",
        "desc": "[ChangeMe] 本规则由 snapshot_parser.py 生成，请根据需要修改",
        "matches": matches,
        # 其它字段留空示例
        "activityIds": [],
        "exampleUrls": [],
        "snapshotUrls": [],
    }
    return {
        "groups": [
            {
                "key": 1,
                "name": "[ChangeMe] 组名称",
                "desc": "[ChangeMe]",
                "rules": [rule],
            }
        ]
    }


def main():
    url = None
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        # 如果没有命令行参数，交互式询问用户
        try:
            url = input("请输入 GKD 快照链接 (或按 Enter 退出)：").strip()
        except EOFError:
            pass
    if not url:
        print("用法: python snapshot_parser.py <快照链接>\n示例: python snapshot_parser.py https://i.gkd.li/i/12345678")
        sys.exit(1)
    print("正在抓取", url)
    data = fetch_snapshot_data(url)
    if not data:
        print("未能获取快照数据，链接可能已失效。")
        sys.exit(1)
    nodes = data.get("nodes", [])
    print(f"提取到 {len(nodes)} 个节点")
    draft = nodes_to_rule(nodes)
    output = json.dumps(draft, ensure_ascii=False, indent=2)
    print(output)
    # 也可以写入文件
    Path("./snapshot_rule_draft.json").write_text(output, encoding="utf-8")
    print("草稿已保存为 snapshot_rule_draft.json")


if __name__ == "__main__":
    main()
