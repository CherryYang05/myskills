"""Stand-in for a published figure. The specimen talk has no paper to extract from, so this script draws a
typical four-panel journal figure from the same data; the deck then treats it exactly like an extracted one."""
import json, pathlib, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = pathlib.Path(__file__).parent; F = json.load(open(H / "facts.json")); v = lambda k: F[k]["value"]
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(8, 6), dpi=250)
def panel(a, title, groups, keys):
    for i, (g, (kw, kb)) in enumerate(zip(groups, keys)):
        for j, (k, c) in enumerate(((kw, "0.25"), (kb, "0.7"))):
            a.bar(i+j*0.36-0.18, v(k), 0.34, color=c, yerr=[[v(k)-v(k+"_lo")], [v(k+"_hi")-v(k)]], capsize=2, error_kw={"lw": .8})
    a.set_xticks(range(len(groups))); a.set_xticklabels(groups); a.set_ylim(0, 16); a.set_ylabel("Callback rate (%)"); a.set_title(title, loc="left", fontsize=10)
panel(ax[0, 0], "A. All résumés", ["All"], [("rate_white", "rate_black")])
panel(ax[0, 1], "B. By city", ["Boston", "Chicago"], [("rate_white_boston", "rate_black_boston"), ("rate_white_chicago", "rate_black_chicago")])
panel(ax[1, 0], "C. By résumé quality", ["Lower", "Higher"], [("rate_white_low", "rate_black_low"), ("rate_white_high", "rate_black_high")])
ax[1, 1].axis("off")
ax[1, 1].text(0, .8, "Dark bars: White-sounding names\nLight bars: African-American-sounding names\nError bars: 95% Wilson intervals", va="top", fontsize=9)
fig.tight_layout(); fig.savefig(H / "assets/paper_fig2.png"); print("figure written")
