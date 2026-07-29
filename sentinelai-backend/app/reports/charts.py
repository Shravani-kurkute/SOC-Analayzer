import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

plt.style.use("dark_background")


def _figure():
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("#333")
    ax.spines["left"].set_color("#333")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    return fig, ax


def bar_chart(labels: list, values: list, title: str = "", xlabel: str = "", ylabel: str = "") -> bytes:
    fig, ax = _figure()
    bars = ax.bar(labels, values, color="#00F5FF", edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                str(val), ha="center", va="bottom", fontsize=9, color="white")
    ax.set_title(title, color="white", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def pie_chart(labels: list, values: list, title: str = "") -> bytes:
    fig, ax = _figure()
    colors_pie = ["#00F5FF", "#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#FF6B6B"]
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%",
        colors=colors_pie[:len(labels)], startangle=90,
        textprops={"color": "white", "fontsize": 9},
        wedgeprops={"edgecolor": "#1a1a2e", "linewidth": 1},
    )
    ax.set_title(title, color="white", pad=12)
    ax.legend(wedges, labels, loc="upper right", bbox_to_anchor=(1.3, 1.0), fontsize=8)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def line_chart(labels: list, values: list, title: str = "", xlabel: str = "", ylabel: str = "") -> bytes:
    fig, ax = _figure()
    ax.plot(labels, values, color="#00F5FF", linewidth=2, marker="o", markersize=4)
    ax.fill_between(range(len(values)), values, alpha=0.1, color="#00F5FF")
    ax.set_title(title, color="white", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def area_chart(labels: list, values: list, title: str = "", xlabel: str = "", ylabel: str = "") -> bytes:
    fig, ax = _figure()
    ax.fill_between(range(len(values)), values, alpha=0.3, color="#00F5FF")
    ax.plot(range(len(values)), values, color="#00F5FF", linewidth=2)
    ax.set_title(title, color="white", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def heatmap(data: list[list], row_labels: list, col_labels: list, title: str = "") -> bytes:
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    im = ax.imshow(data, cmap="viridis", aspect="auto")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.yticklabels), color="white")
    ax.set_xticks(range(len(col_labels)))
    ax.set_yticks(range(len(row_labels)))
    ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=8, color="white")
    ax.set_yticklabels(row_labels, fontsize=8, color="white")
    ax.set_title(title, color="white", pad=12)
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            ax.text(j, i, str(data[i][j]), ha="center", va="center", fontsize=8, color="white")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def generate_report_charts(report_data: dict, report_type: str) -> dict[str, bytes]:
    charts = {}
    if report_type == "executive":
        if report_data.get("top_attack_types"):
            items = report_data["top_attack_types"]
            charts["attack_types"] = bar_chart(
                [i["name"] for i in items], [i["count"] for i in items],
                "Top Attack Types", "Attack Type", "Count",
            )
        if report_data.get("top_risks"):
            items = report_data["top_risks"]
            charts["top_risks"] = bar_chart(
                [i["name"] for i in items], [i["count"] for i in items],
                "Top Risks", "Risk", "Count",
            )
    elif report_type == "threat":
        if report_data.get("risk_distribution"):
            items = report_data["risk_distribution"]
            charts["risk_distribution"] = pie_chart(
                [i["name"] for i in items], [i["count"] for i in items],
                "Risk Distribution",
            )
        if report_data.get("attack_timeline"):
            items = report_data["attack_timeline"]
            charts["attack_timeline"] = area_chart(
                [i["time"] for i in items], [i["count"] for i in items],
                "Attack Timeline", "Time", "Count",
            )
    return charts
