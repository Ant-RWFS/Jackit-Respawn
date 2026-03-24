import base64
from io import BytesIO
import matplotlib.pyplot as plt
import flet as ft


class Diagram(ft.Image):
    def __init__(self, page, config):
        super().__init__(
            expand=True,
            src_base64="",
            fit=ft.ImageFit.CONTAIN
        )
        self.page = page
        self.config = config
        self.signal_list = []
        self.init_placeholder()

    def diagram_layout(self, data=None):
        fig, ax = plt.subplots(figsize=(8, 4))
        if data and isinstance(data, list) and len(data) > 0:
            color = self.page.theme.color_scheme.primary
            node_text_color = self.page.theme.color_scheme.on_primary
            text = self.config.RESC['text']['diagram']['signal']
            self.signal_list = data
            x = list(range(len(data)))
            ax.plot(x, data, linewidth=0.5, color=color, marker='o', markersize=5)

            for i, (xi, yi) in enumerate(zip(x, data)):
                offset = 5 if yi < 240 else -10
                ax.annotate(str(yi),
                            xy=(xi, yi),
                            xytext=(xi, yi + offset),
                            textcoords='data',
                            fontsize=8,
                            color=node_text_color,
                            bbox=dict(alpha=0))

            ax.set_xlabel(text['x'], color=color)
            ax.set_ylabel(text['y'], color=color)
            ax.set_title(text['title'], color=color)
            ax.tick_params(colors=color)
            ax.grid(True, linestyle='--', alpha=0.6, color=color)

            for spine in ax.spines.values():
                spine.set_color(color)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_position(('data', 0))
            ax.spines['bottom'].set_position(('data', 0))
            ax.set_xlim(0, len(data) - 1)
            ax.set_ylim(0, 255)
            ax.set_yticks(range(0, 256, 32))

            if len(data) <= 30:
                ax.set_xticks(range(len(data)))
                ax.set_xticklabels(range(len(data)), ha='right')
            else:
                step = max(1, len(data) // 20)
                xticks = range(0, len(data), step)
                ax.set_xticks(xticks)
                ax.set_xticklabels(xticks, ha='right')
                ax.tick_params(axis='x', labelsize=8)

        else:
            ax.axis('off')

        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', transparent=True)
        buf.seek(0)
        plt.close(fig)
        return buf

    def init_placeholder(self):
        buf = self.diagram_layout()
        self.src_base64 = base64.b64encode(buf.read()).decode()
        self.update()

    def update_diagram(self, data: list):
        buf = self.diagram_layout(data)
        self.src_base64 = base64.b64encode(buf.read()).decode()
        self.update()
