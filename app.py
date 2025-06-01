import streamlit as st
import subprocess
import uuid
import json
import os
import glob
import pandas as pd

def clear_workspace():
    workspace_dir = "./workspace"

    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        return
    # 如果存在，清除所有文件（不管文件类型）
    for fname in os.listdir(workspace_dir):
        fpath = os.path.join(workspace_dir, fname)
        try:
            if os.path.isfile(fpath):
                os.remove(fpath)
        except Exception as e:
            st.error(f"无法删除 {fpath}: {e}")


st.title("Data Scientist Agent")

# 1.用户输入指令 添加系统提示词为了统一输出格式为JSON格式，方便前端显示
system_prefix = """你运行在 Streamlit 前端环境中，请严格遵守以下输出规范：

# 输出规则
1. 必须将向用户展示的结果(包括但不限于图像，表格，文字等)保存为JSON文件，按向用户展示的顺序先后保存，若生成图像或者表格及其他可视化内容，新写一个JSON文件以text类型保存，JSON文件保存路径为 `./workspace/output_<类型>_<序号>.json`
2. JSON结构示例：
   {
       "type": "<text|image|table>",
       "data": {
           "content": "文字内容/图像路径/DataFrame字典",
           "title": "可选的展示标题",
           "description": "可选的图表简单说明"
       },
       "timestamp": "生成时间(ISO格式)"
   }
"""
requirement = system_prefix + "\n" +st.text_area("请输入任务需求（必填）", placeholder="例如：请分析我上传的数据并预测目标变量")
# 2.上传文件
uploaded_file = st.file_uploader("请上传你的数据文件（CSV 格式）", type=["csv"])
# 3.是否使用工具
use_tools = st.radio("是否启用工具", ["否（基础版）", "是（增强版）"], index=0)
# 4.模式选择
react_mode = st.radio("思考模式", ["plan_and_act", "react"], index=0)


# 5.用户点击“运行智能体”，调用后端逻辑，使Agent生成json文件
if st.button("运行智能体"):
    is_success = False
    if not requirement.strip():
        st.warning("请输入任务指令！")
    else:
        # 清除旧文件
        clear_workspace()

        # 如果上传文件，保存文件并得到文件地址，将地址写入prompt
        file_path = None
        if uploaded_file:
            filename = f"upload_{uuid.uuid4().hex[:8]}.csv"
            os.makedirs("tmp", exist_ok=True)
            file_path = os.path.join("tmp", filename)
            requirement += f"\n数据路径: {file_path}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        # 构建执行命令
        script = "machine_learning_with_tools.py" if "是" in use_tools else "machine_learning.py"
        command = ["python", script, requirement, react_mode]

        st.info("正在分析，请稍后:")
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            st.success("✅ 执行完成！")
            st.text_area("控制台输出", result.stdout + "\n" + result.stderr,
                         height=300)  # 显示控制台输出，方便用户分析
            is_success = True

        except Exception as e:
            st.error(f"❌ 执行失败: {e}")

    # 如果执行成功，显示分析结果(将json文件展示给用户)
    if is_success:
        st.title(" 分析结果：")
        # 按创建时间顺序读取json文件
        workspace="./workspace"
        json_files = glob.glob(os.path.join(workspace, "output_*.json"))

        # 排序：按文件系统的创建时间
        sorted_files = sorted(json_files, key=os.path.getctime, reverse=False)
        outputs = []
        for fpath in sorted_files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    outputs.append(data)
            except Exception as e:
                st.warning(f"读取 {fpath} 失败: {e}")

        if not outputs:
            st.info("未找到任何输出 JSON 文件。请先运行智能体任务生成结果。")
        else:
            for output in outputs:
                otype = output.get("type", "")
                data = output.get("data", {})
                title = data.get("title", "未命名结果")
                content = data.get("content", "")
                desc = data.get("description", "")

                st.markdown("---")
                st.markdown(f"#### {title}")

                if otype == "text":
                    st.write(content)
                elif otype == "image" or otype == "plot":
                    st.image(content, caption=desc)
                elif otype == "table":
                    try:
                        df = pd.DataFrame.from_dict(content)
                        st.dataframe(df)
                        st.caption(desc)
                    except Exception as e:
                        st.error(f"表格格式错误: {e}")
                else:
                    st.warning(f"未知类型: {otype}")


