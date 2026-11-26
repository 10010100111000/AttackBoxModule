#!/usr/bin/env python3
"""Generate stable NodeBlog Flags and matching learner Challenge Markdown."""
from __future__ import annotations
import argparse, base64, json, re, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "nodeblog"
FLAGS = LAB / "flags"
RELEASES = FLAGS / "releases"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\{[a-z2-7]{16}\}$")
FENCE = chr(96) * 3

def new_flag():
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"

def challenge_markdown(summary, level, intro, stages):
    lines = ["---", f"summary: {summary}", f"level: {level}", "lab: nodeblog", "---", "",
             "# 场景", "", intro, "", "# 任务", "",
             "通过网站的真实功能完成目标。每个阶段都需要提交对应 Flag；后续挑战会重新考察前面阶段，作为复习和综合验证。", ""]
    for title, prompt, answer in stages:
        lines.extend([FENCE + "quiz", f"title: {title}", "kind: flag", "prompt: |",
                      f"  {prompt}", f'answer: "{answer}"', "match: trim",
                      "hint: 从应用实际提供的功能和数据流入手，先观察，再验证。",
                      FENCE, ""])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    version = parser.parse_args().version
    if not VERSION_RE.fullmatch(version):
        raise SystemExit("version must be numeric semver, e.g. 1.0.0")
    RELEASES.mkdir(parents=True, exist_ok=True)
    manifest_path = RELEASES / f"{version}.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        flags = manifest.get("flags", {})
        if manifest.get("version") != version or set(flags) != {"flag01", "flag02", "flag03"}:
            raise SystemExit("invalid existing release manifest")
        if len(set(flags.values())) != 3 or not all(FLAG_RE.fullmatch(v) for v in flags.values()):
            raise SystemExit("manifest contains invalid or duplicate Flags")
        action = "reused"
    else:
        values = [new_flag() for _ in range(3)]
        while len(set(values)) != 3:
            values = [new_flag() for _ in range(3)]
        flags = dict(zip(("flag01", "flag02", "flag03"), values))
        manifest = {"version": version, "format": "TTP{16-lowercase-base32}", "flags": flags}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        action = "generated"

    (FLAGS / "flag01.txt").write_text(flags["flag01"] + "\n", encoding="utf-8")
    (FLAGS / "flag02.txt").write_text(flags["flag02"] + "\n", encoding="utf-8")
    (FLAGS / "user.txt").write_text(flags["flag03"] + "\n", encoding="utf-8")

    docs = {
        ROOT / "challenges/authentication/nodeblog-nosql/NoSQL Authentication Bypass.md":
            challenge_markdown("调查博客登录行为，完成第一阶段认证挑战。", "easy",
                "一个社区博客开放了文章浏览和作者登录功能。请从普通访问者的视角观察登录请求与应用响应，找到进入受保护作者内容的方法。",
                [("Flag 01 — Protected Staff Note", "进入受保护的编辑团队内容，提交其中的第一枚 Flag。", flags["flag01"])]),
        ROOT / "challenges/file-security/nodeblog-xxe/XXE Source Disclosure.md":
            challenge_markdown("复习认证绕过，并调查 XML 导入和外部实体解析。", "medium",
                "博客提供 XML 文章导入功能。完成认证目标后，继续观察导入数据如何被服务端解析，以及解析结果如何进入文章编辑器。",
                [("Flag 01 — Authentication Review", "重新完成认证阶段，提交受保护内容中的第一枚 Flag。", flags["flag01"]),
                 ("Flag 02 — XML Disclosure", "利用 XML 导入处理过程读取专用本地数据文件，提交第二枚 Flag。", flags["flag02"])]),
        ROOT / "challenges/code-execution/nodeblog-deserialization/Unsafe Cookie Deserialization.md":
            challenge_markdown("综合考察 NoSQL 认证绕过、XXE 和不安全 Cookie 反序列化。", "hard",
                "你将对同一个博客应用进行完整 Web 安全评估。重新验证认证边界与 XML 导入行为，再调查浏览器会话 Cookie 的生成、解析和信任过程。",
                [("Flag 01 — Authentication Review", "重新完成认证阶段，提交受保护内容中的第一枚 Flag。", flags["flag01"]),
                 ("Flag 02 — XML Disclosure Review", "重新完成 XML 外部实体读取阶段，提交第二枚 Flag。", flags["flag02"]),
                 ("Flag 03 — Web Execution", "利用会话处理中的真实漏洞取得 Web 服务执行能力，提交最终 Flag。", flags["flag03"])])
    }
    for path, content in docs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"NodeBlog release {version}: {action}; 3 unique 80-bit Flags")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    print(f"Generated {len(docs)} Challenge documents; Flag values are not printed.")

if __name__ == "__main__":
    main()
