"""Módulo de diagnósticos visuales, econométricos y gráficos de optimización."""

from __future__ import annotations

from src.analytics.visual_diagnostics import (
    plot_gauss_markov_quad,
    plot_bayesian_update_curve,
    plot_pca_biplot_stops,
    plot_delay_heatmap,
    plot_causal_dag_visual,
    plot_milp_dispatch_bars,
    plot_unconstrained_convergence,
    plot_heuristic_convergence,
)

__all__ = [
    "plot_gauss_markov_quad",
    "plot_bayesian_update_curve",
    "plot_pca_biplot_stops",
    "plot_delay_heatmap",
    "plot_causal_dag_visual",
    "plot_milp_dispatch_bars",
    "plot_unconstrained_convergence",
    "plot_heuristic_convergence",
]
