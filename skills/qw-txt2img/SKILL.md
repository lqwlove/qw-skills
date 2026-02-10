---
name: qw-txt2img
description: 使用工作流, 根据文字生成图片。
---

# Text-to-Image

使用ComfyUI工作流生成图片。

## Script Directory

**Agent Execution**:
1. `SKILL_DIR` = this SKILL.md file's directory
2. Script path = `${SKILL_DIR}/scripts/main.py`

## Usage

```bash
# Basic usage
python ${SKILL_DIR}/scripts/main.py --prompt "一个女孩在海边散步"

# With custom dimensions
python ${SKILL_DIR}/scripts/main.py --prompt "夕阳下的城市风光" --width 1920 --height 1080

```

## Options

| Option | Description |
|--------|-------------|
| `--prompt <text>` | Prompt text (required) |
| `--width <int>` | Image width, default 1080 |
| `--height <int>` | Image height, default 1920 |

## Configuration

Edit `${SKILL_DIR}/scripts/main.py` to configure:

| Variable | Description |
|----------|-------------|
| `API_KEY` | API key |
| `WORKFLOW_ID` | Workflow ID to use |
| `API_BASE` | API base URL |

## Output

- Images saved to `output/` folder
- Filenames auto-increment (image_1.png, image_2.png, etc.)
