from pyecharts import options as opts
from pyecharts.charts import Line
from streamlit_echarts import st_pyecharts, st_echarts

def create_example_graph():
    # Example data
    x = [0, 1, 2, 3, 4, 5]
    y = [10, 8, 5, 0, -3, -5]

    # Create chart
    graph = (
        Line()
        .add_xaxis(x)
        .add_yaxis("Shear Force", y_axis=y, is_symbol_show=False,
                   areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
        .set_global_opts(title_opts=opts.TitleOpts(title="Shear Force"))
    )

    # Display in Streamlit
    st_pyecharts(chart=graph)  # ✅ chart=graph is required

# create_example_graph()


def create_sfd_plotly():
    import streamlit as st
    import plotly.graph_objects as go

    # Example data
    x = [0, 1, 2, 3, 4, 5]
    y = [10, 8, 5, 0, -3, -5]

    # Create Plotly figure
    fig = go.Figure()

    # Add Shear Force line with area fill
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines",  # no markers
        fill="tozeroy",  # area fill to y=0
        name="Shear Force",
        line=dict(color="blue")
    ))

    # Customize layout
    fig.update_layout(
        title="Shear Force",
        xaxis_title="Position",
        yaxis_title="Shear Force",
        template="plotly_white",
        height=400,
        width=700
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def create_echart_example():
    options = {
        "title": {"text": "折线图堆叠"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["邮件营销", "联盟广告", "视频广告", "直接访问", "搜索引擎"]},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "邮件营销",
                "type": "line",
                "stack": "总量",
                "data": [120, 132, 101, 134, 90, 230, 210],
            },
            {
                "name": "联盟广告",
                "type": "line",
                "stack": "总量",
                "data": [220, 182, 191, 234, 290, 330, 310],
            },
            {
                "name": "视频广告",
                "type": "line",
                "stack": "总量",
                "data": [150, 232, 201, 154, 190, 330, 410],
            },
            {
                "name": "直接访问",
                "type": "line",
                "stack": "总量",
                "data": [320, 332, 301, 334, 390, 330, 320],
            },
            {
                "name": "搜索引擎",
                "type": "line",
                "stack": "总量",
                "data": [820, 932, 901, 934, 1290, 1330, 1320],
            },
        ],
    }
    st_echarts(options=options, height="400px")