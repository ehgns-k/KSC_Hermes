"""Figure 1: Hermes baseline vs CEM. Plain matplotlib."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcdefaults()
fig, ax = plt.subplots(figsize=(7.2, 3.0))
ax.set_xlim(0, 100)
ax.set_ylim(0, 46)
ax.axis("off")
BOX = dict(boxstyle="round,pad=0.5", fc="white", ec="black", lw=0.8)
ARROW = dict(arrowstyle="->", lw=0.8, shrinkA=4, shrinkB=4)
X = [8, 30, 52, 74, 92]          # shared column grid for both panels


def box(x, y, text):
    return ax.text(x, y, text, ha="center", va="center", fontsize=7, bbox=BOX)


def chain(boxes):
    for a, b in zip(boxes, boxes[1:]):
        ax.annotate("", xy=(0, 0.5), xycoords=b, xytext=(1, 0.5), textcoords=a, arrowprops=ARROW)


ax.text(0, 44, "(a) Hermes", fontsize=8.5, fontweight="bold")
chain([box(X[0], 37, "Session\nnotes"), box(X[1], 37, "LLM edits MEMORY.md\n(add/patch/remove)"),
       box(X[2] + 5, 37, "Over 2,200 chars:\nLLM merges or deletes")])
ax.text(X[3] - 2, 37, "(every session)", fontsize=7, va="center")
chain([box(X[0], 27, "Previous\nsummary"), box(X[1], 27, "+ new turns"),
       box(X[2] + 5, 27, "LLM rewrites\nthe summary")])
ax.text(X[3] - 2, 27, "(every compaction)", fontsize=7, va="center")

ax.text(0, 18, "(b) CEM", fontsize=8.5, fontweight="bold")
chain([box(X[0], 8, "Session\nnotes"), box(X[1], 8, "1. Extract (LLM)\nentity, attr, scope,\nvalue, prev. value"),
       box(X[2], 8, "2. Ground\ndrop values not\nin the source"), box(X[3], 8, "3. Merge\nversion chain per\n(entity, attr, scope)"),
       box(X[4] + 1, 8, "4. Pack\nfewest chars\nfirst")])

out = Path(__file__).resolve().parents[2] / "paper" / "figures"
fig.savefig(out / "fig1_method_overview.png", dpi=300, bbox_inches="tight")
fig.savefig(out / "fig1_method_overview.pdf", bbox_inches="tight")
