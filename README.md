# ai-ui-forge

> 一个用来「让 AI 别再瞎猜设计」的 skill：**先落令牌，再写结构，最后过清单**。

给 Claude Code / Codex / Cursor / DSH 这类 agent 用的技能包。装上之后，
它做前端页面时会先产 `design-tokens.json`，再一屏一板块地写，交付前自己过一遍检查清单——
而不是一口气吐出 4000 行「能用但丑」的 HTML。

## 它解决的三个问题

| 缺口 | 表现 | 这个 skill 的落点 |
|---|---|---|
| 上下文 | 不知道你的栅格、字体、色板，只能用模型默认审美 | `design-tokens.json`（亮暗两套 + 语义命名） |
| 结构 | 整页丢过去，层级瞎猜，第 3 页开始风格漂移 | 一屏一板块 + 结构先于样式 |
| 验收 | 对比度、暗色、焦点态没人查就上线 | 4 组 30 条自检清单，逐条写结论 |

## 目录

```
SKILL.md                     技能正文：铁律 / 输入契约 / 六步流程 / 输出契约 / 反模式
references/
  styles.json                8 套风格预设（亮暗双套配色、字体配对、圆角、密度、禁用项）
  checklist.md               交付自检清单（视觉 / 交互 / 无障碍 / 工程 / 一致性）
scripts/
  tokens.py                  按预设生成 design-tokens.json，支持覆盖主色
examples/
  design-tokens.json         生成样例（dark-console 预设）
  index.html                 样板页：单文件、暗色自适应、键盘可达、无外链资源
```

## 用法

**1. 生成令牌**

```bash
python scripts/tokens.py --list
python scripts/tokens.py --preset calm-wellness --primary "#2F6B4F" -o design-tokens.json
```

8 套预设：`neutral-pro`（SaaS 默认）· `editorial-warm`（杂志）· `dark-console`（开发者工具）·
`calm-wellness`（疗愈低饱和）· `brutalist-bold`（新粗野）· `luxe-mono`（高级黑白）·
`playful-soft`（轻盈活泼）· `gradient-startup`（创业渐变）。

**2. 让 agent 读 `SKILL.md`**

把整个目录放进你的 skills 目录（或直接把 `SKILL.md` 的内容作为系统提示的一部分）。
它会在动手前先问你：产品一句话、页面类型、风格取向、品牌色、技术栈、语言与字体。

**3. 看样板页**

`examples/index.html` 双击即开——它就是按 `examples/design-tokens.json` 渲染的，
可以用它判断这套令牌的观感是否适合你的项目。换风格只改令牌，不碰样式表。

## 设计取向（为什么这么定）

- **令牌是唯一真源**：组件里出现 `#hex` 或魔法 `px` 就算违约。
- **间距只允许 8pt 刻度**：4/8/12/16/24/32/48/64/96，别的一律不认。
- **圆角 ≤ 3 档、阴影 ≤ 2 档**：一致性靠限制，不靠审美。
- **组件库优先**：指定 shadcn/ui 或 HeroUI，明令「除非必要不自造组件」；图标只用 lucide/tabler。
- **模型只写内容与结构**：排版交给本地渲染，同一份内容 token 能省十倍。

## 已知边界

- 8 套预设的色值是**起点**，不是从真实产品采样来的；换品牌色建议只替换 `primary` / `accent`。
- 不依赖任何 Figma 链路（Figma MCP / Figma Make 的产出稳定性在实践中偏差较大），纯 HTML + JSON 闭环。
- 自检清单是给 agent 用的判据，不是自动检测器——它得自己量对比度、自己数圆角档位。

## License

MIT。参考来源（B站视频）见发布文案，本仓库代码与文案为原创整理。
