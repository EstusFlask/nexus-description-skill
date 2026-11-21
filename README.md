# Nexus Description Skill

把 Nexus Mods description 整理成清楚、可读、重点突出的页面。支持参考页面风格、原生 BBCode、双语分区、贡献者招募强调，以及获授权更新后的实际页面核对。

This Codex skill helps draft and restyle Nexus Mods descriptions, learn from reference layouts, highlight important notices, and verify the saved public page when publishing is requested.

## Codex marketplace 结构

```text
.agents/plugins/marketplace.json
plugins/nexus-description/
  .codex-plugin/plugin.json
  skills/nexus-description/
    SKILL.md
    agents/openai.yaml
    references/
      layout-patterns.md
      nexus-editor.md
    scripts/check_bbcode.py
```

仓库采用 [Codex repo marketplace 格式](https://developers.openai.com/plugins/build/plugins)。marketplace 名为 `nexus-description-skill`，插件和技能名均为 `nexus-description`；清单通过相对路径指向插件，无需修改成你的本机绝对路径。

在支持该格式的 Codex 客户端中添加本仓库作为 marketplace 来源，再选择安装 **Nexus Description 排版**。具体入口依客户端版本而异。也可将 `plugins/nexus-description/skills/nexus-description/` 作为独立 skill 安装。此仓库不会自动修改你的 Codex 配置或连接 Nexus 账号。

## 使用示例

```text
使用 $nexus-description，参考这两个页面重排我的 Nexus description，
把接手维护者招募突出显示；保留已有安装说明和署名，并更新指定页面。
```

```text
使用 $nexus-description，把这份 Mod 介绍整理成中英双语 BBCode，
只生成草稿，不更新线上。
```

技能会按需要读取两个参考文件。配色、章节数量、双语形式和招募框是可调整的设计选择；不会把其他 Mod 的功能、素材或本机发布规则套到你的项目。页面排版与 Mod 构建、文件上传、版本或权限变更分别处理。

## 验证

结构检查器仅使用 Python 标准库：

```powershell
python plugins/nexus-description/skills/nexus-description/scripts/check_bbcode.py path/to/description.bbcode
python -m unittest discover -s tests -v
```

检查器支持常见标签的嵌套、列表项位置和空链接目标，忽略未知标签及代码块里的字面语法；它不是完整的 Nexus 解析器，不检查链接可达性，也不证明页面已保存。线上效果仍需在实际页面核对并留图。

本仓库不附带 MCP 服务、浏览器扩展或账号凭证。实际页面修改使用当前 Codex 环境中可用的浏览器／连接工具；没有可用会话时仍可生成 BBCode 草稿。
