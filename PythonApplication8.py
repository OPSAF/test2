import streamlit as st
from manim import *
import tempfile
import os
import numpy as np

# 1. 尝试渲染一个最简单的 Manim 场景
class SimpleScene(Scene):
    def construct(self):
        # 渲染一个正方形
        square = Square(side_length=2, color=BLUE)
        self.play(Create(square), run_time=1)
        self.wait(1)

# 2. 核心渲染和文件处理逻辑 (必须使用临时目录)
st.title("Manim/Streamlit 环境测试")
st.info("如果看到一个蓝色正方形的动画视频，说明环境配置成功！")

# 使用 Streamlit 按钮触发渲染（避免 Streamlit 启动循环报错）
if st.button("开始 Manim 测试渲染"):
    with st.spinner("正在渲染 Manim 动画..."):
        # 设置 Manim 配置，确保输出到临时目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            config.media_dir = tmp_dir
            config.pixel_height = 480 
            config.pixel_width = 854
            config.frame_rate = 15
            config.verbosity = "WARNING" # 减少日志
            
            try:
                scene = SimpleScene()
                scene.render()
                
                # 获取视频路径
                video_path = str(scene.renderer.file_writer.movie_file_path)
                
                # 显示视频
                st.video(video_path)
                st.success("🎉 渲染成功！Manim 环境已修复。")
                
            except Exception as e:
                st.error(f"Manim 渲染失败，错误信息: {e}")
                st.warning("如果失败，可能是 Streamlit Cloud 容器的内存或 FFmpeg 路径问题。")
