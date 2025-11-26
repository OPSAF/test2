import streamlit as st
import random
import numpy as np
from manim import *
import tempfile
import os

# --- 页面配置 ---
st.set_page_config(
    page_title="数据科学魔法：蒙特卡洛求π",
    page_icon="🎯",
    layout="wide"
)

# --- 标题与介绍 ---
st.title("🎯 蒙特卡洛模拟：用随机性寻找 $\pi$")
st.markdown("""
> **什么是蒙特卡洛方法？** > 简单来说，就是通过大量的“随机实验”来估算结果。
> 想象你在一个正方形里画了一个圆，然后蒙着眼睛往里扔飞镖。
> 只要飞镖扔得足够多，落在圆内的飞镖比例，就能帮我们算出圆周率 $\pi$！
""")

st.divider()

# --- 侧边栏控制 ---
with st.sidebar:
    st.header("⚙️ 实验参数设置")
    total_points = st.slider("投掷飞镖的总数量 (N)", 10, 2000, 500, step=10)
    st.info("注意：Manim渲染视频需要时间，为了演示流畅，建议先用较小的数字（如 100-500）尝试。")
    
    run_btn = st.button("🚀 开始模拟实验", type="primary")

# --- 核心逻辑 ---
col1, col2 = st.columns([1.5, 1])

if run_btn:
    with col1:
        st.subheader("📺 实时生成动画 (Manim Render)")
        progress_bar = st.progress(0, text="正在渲染动画...")

        # --- Manim 场景定义 ---
        # 我们在一个临时目录中生成视频，避免污染文件夹
        class MonteCarloScene(Scene):
            def construct(self):
                # 1. 设置画布
                self.camera.background_color = "#0E1117" # 匹配 Streamlit 深色模式
                
                # 定义几何图形 (半径设为3)
                radius = 3
                circle = Circle(radius=radius, color=BLUE, stroke_width=4)
                square = Square(side_length=radius*2, color=WHITE, stroke_opacity=0.5)
                
                # 添加文字说明
                label = Text("Monte Carlo Simulation", font_size=36).to_edge(UP)
                
                self.play(Create(square), Create(circle), Write(label), run_time=1.5)
                
                # 2. 生成随机点并决定颜色
                points_group = VGroup()
                inside_count = 0
                
                # 为了视频时长适中，无论用户选多少点，视频里最多只展示前150个点的动画过程
                # 剩下的点瞬间显示
                animation_limit = 100 
                
                all_dots = []
                
                for i in range(total_points):
                    x = random.uniform(-radius, radius)
                    y = random.uniform(-radius, radius)
                    
                    # 判断是否在圆内 (x^2 + y^2 <= r^2)
                    is_inside = (x**2 + y**2) <= (radius**2)
                    if is_inside:
                        inside_count += 1
                        col = GREEN
                    else:
                        col = RED
                        
                    dot = Dot(point=[x, y, 0], radius=0.05, color=col)
                    all_dots.append(dot)

                # 3. 动画逻辑
                # 前N个点带动画效果
                self.play(
                    AnimationGroup(
                        *[Create(d) for d in all_dots[:animation_limit]],
                        lag_ratio=0.1
                    ),
                    run_time=3
                )
                
                # 剩下的点如果很多，一次性淡入
                if total_points > animation_limit:
                    remaining_dots = VGroup(*all_dots[animation_limit:])
                    self.play(FadeIn(remaining_dots), run_time=1)
                
                self.wait(1)

        # --- 渲染 Manim ---
        # 这是一个小技巧：使用 temp_dir 来处理 Manim 的输出
        # --- 渲染 Manim (确保使用临时目录) ---
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 这是一个关键配置：告诉 Manim 把所有媒体文件写到临时目录
            config.media_dir = tmp_dir
            config.pixel_height = 720 
            config.pixel_width = 1280
            config.frame_rate = 30
            config.verbosity = "ERROR" # 减少日志输出，防止 Streamlit 日志过多
            
            try:
                scene = MonteCarloScene()
                # 渲染
                scene.render() 
                
                # 获取生成的视频路径
                # 由于我们设置了 config.media_dir，所以路径会自动指向 tmp_dir
                video_path = str(scene.renderer.file_writer.movie_file_path)
                
                # ... (Streamlit 展示视频 st.video(video_path))
                
                progress_bar.progress(100, text="渲染完成！")
                st.video(video_path)
                
            except Exception as e:
                st.error(f"Manim 渲染出错: {e}")
                st.warning("请检查是否已安装 FFmpeg。")

    with col2:
        st.subheader("📊 实验数据分析")
        
        # 纯 Python 计算逻辑 (用于数据展示，不依赖 Manim 的视觉限制)
        sim_inside = 0
        sim_points = []
        for _ in range(total_points):
            x = np.random.uniform(-1, 1)
            y = np.random.uniform(-1, 1)
            if x**2 + y**2 <= 1:
                sim_inside += 1
        
        my_pi = 4 * (sim_inside / total_points)
        real_pi = np.pi
        error = abs((my_pi - real_pi) / real_pi) * 100

        # 使用 Streamlit 的 Metric 组件展示结果
        st.metric(label="投掷总数 (N)", value=total_points)
        st.metric(label="圆内点数", value=sim_inside)
        
        st.divider()
        
        st.markdown("### 你的计算结果：")
        st.latex(r"\pi \approx 4 \times \frac{\text{圆内点数}}{\text{总点数}}")
        
        c1, c2 = st.columns(2)
        c1.metric(label="估算的 π", value=f"{my_pi:.4f}", delta=f"{my_pi-real_pi:.4f}")
        c2.metric(label="真实 π", value=f"{real_pi:.4f}")
        
        st.write(f"**误差率:** `{error:.2f}%`")
        
        if error < 1:
            st.success("🎉 太棒了！你的估算非常精准！")
        elif error < 5:
            st.warning("👌 不错，虽然有一点偏差，但这是随机性的魅力。")
        else:
            st.error("📉 误差有点大，试着增加投掷数量 (N) 看看？")

else:
    # 初始状态占位符
    with col1:
        st.info("👈 请在左侧调整参数，然后点击“开始模拟实验”")
        # 展示一个静态示意图作为占位
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 300px; border: 2px dashed gray; border-radius: 10px;">
                <h3>等待运行...</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )

# --- 教育性页脚 ---
st.divider()
with st.expander("🎓 为什么这能算出 π？(点击展开原理)"):
    st.markdown("""
    1.  **面积法**：
        * 正方形的边长设为 $2r$，面积 = $(2r)^2 = 4r^2$。
        * 内切圆的半径为 $r$，面积 = $\pi r^2$。
    2.  **比例关系**：
        * $\frac{\text{圆的面积}}{\text{正方形面积}} = \frac{\pi r^2}{4r^2} = \frac{\pi}{4}$
    3.  **蒙特卡洛模拟**：
        * 如果点是均匀随机分布的，那么落在圆内的点的概率就等于圆的面积占比。
        * $\frac{\text{圆内点数}}{\text{总点数}} \approx \frac{\pi}{4}$
    4.  **结论**：
        * $\pi \approx 4 \times \frac{\text{圆内点数}}{\text{总点数}}$
    """)

