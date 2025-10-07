"""UI helper builders used across section factories."""

import gradio as gr
from .i18n import t


def navigation_row(lang: str = "en", show_back: bool = True, next_label: str | None = None):
    """Return a tuple (back_button, next_button) of Gradio Button instances contained in a Row.

    This centralizes consistent labels and classes so other modules can reuse it.
    """
    back = gr.Button(t("back", lang), elem_classes="back-button") if show_back else None
    next_lab = next_label or t("next", lang)
    # Create the buttons but do NOT render them here. The caller will place
    # them inside the desired layout (Row/Column) to avoid duplicate rendering
    # inside the same Blocks context.
    nxt = gr.Button(next_lab, variant="primary", elem_classes="next-button")
    return back, nxt


def render_navigation_row(back_btn, next_btn):
    """Place the provided buttons inline inside a Row.

    This should be called from within a Blocks/Column context where rendering
    is allowed. It avoids creating new button instances and ensures the
    layout is consistent across sections.
    """
    # Use two columns so buttons appear side-by-side even if button CSS
    # forces full-width appearance. The next/primary button gets more
    # horizontal space by default.
    with gr.Row():
        if back_btn is not None:
            with gr.Column(scale=1):
                back_btn
        # next button should take more space so it's visually prominent
        with gr.Column(scale=3):
            next_btn

