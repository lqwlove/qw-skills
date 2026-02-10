---
name: qw-image-edit
description: 上传图片并使用RunningHub工作流进行图片编辑，最后下载生成图片到output文件夹。
---

# QW Image Edit

使用RunningHub ComfyUI工作流进行图片编辑。

## Workflow

1. **上传图片**: 调用 `${SKILL_DIR}/scripts/upload.py` 脚本，上传本地图片，保存返回的 `fileName`
2. **执行图生图**: 调用 `${SKILL_DIR}/scripts/img2img.py` 脚本，传入 `fileName` 和提示词，获取返回的**图片URL**
3. **下载图片**: 把返回的图片地址下载下来，存放到项目根目录的output文件夹下

## 需求确认

在执行图生图之前，必须先与用户确认改动细节：

1. **理解用户需求**：询问用户想要做什么改动（如：换背景、改动作、加特效、换风格等）
   - **提示词不参考原图**：根据用户描述的自由想法生成，不受原图内容限制
2. **确认提示词**：与用户确认最终的提示词描述
3. **得到明确同意**：用户确认后才可以继续执行后续步骤

## Agent Steps

When user requests image editing:

1. **需求确认**：先与用户沟通，明确改动内容和提示词

2. Run: `python ${SKILL_DIR}/scripts/upload.py --file <本地图片路径>`
   - Extract the `fileUrl` from the output

3. Run: `python ${SKILL_DIR}/scripts/img2img.py --image <fileUrl> --prompt <提示词>`
   - Extract the **image URL** from the output
   - fileUrl是第一步的返回结果，要取全部的，不要少字符

4. 把第二步返回的图片url下载下来，放到项目根目录的output文件夹下，追加，不要重名

