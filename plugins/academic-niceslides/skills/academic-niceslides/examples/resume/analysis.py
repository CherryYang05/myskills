"""Grounding for the specimen talk. Every number the deck shows is computed here and written to facts.json
as {id: {value, text, how}}. Run: python3 analysis.py"""
import json, pathlib, pandas as pd, statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint, proportions_ztest
H = pathlib.Path(__file__).parent
df = pd.read_csv(H / "data/ResumeNames.csv")
df["y"] = (df.call == "yes").astype(int); df["black"] = (df.ethnicity == "afam").astype(int)
df["high"] = (df.quality == "high").astype(int); df["female"] = (df.gender == "female").astype(int)
df["boston"] = (df.city == "boston").astype(int)
F = {}
def put(k, v, text, how): F[k] = {"value": float(v), "text": text, "how": how}
pct = lambda p: f"{100*p:.1f}%"
def rate(key, g, what):
    k, m = int(g.y.sum()), len(g); p = k/m; lo, hi = proportion_confint(k, m, method="wilson")
    put(key, 100*p, pct(p), f"callbacks / résumés, {what} (n={m})")
    put(key+"_lo", 100*lo, pct(lo), f"Wilson 95% lower bound, {what}"); put(key+"_hi", 100*hi, pct(hi), f"Wilson 95% upper bound, {what}")
    return k, m
put("n", len(df), f"{len(df):,}", "rows in data/ResumeNames.csv")
put("ci_level", 95, "95%", "confidence level of every interval")
kw, mw = rate("rate_white", df[df.black == 0], "White-sounding names")
kb, mb = rate("rate_black", df[df.black == 1], "African-American-sounding names")
put("n_group", mw, f"{mw:,}", "résumés per name group")
gap = F["rate_white"]["value"] - F["rate_black"]["value"]
put("gap_pp", gap, f"{gap:.1f}", "rate_white − rate_black, percentage points")
put("ratio", 100*(F["rate_white"]["value"]/F["rate_black"]["value"]-1), f'{100*(F["rate_white"]["value"]/F["rate_black"]["value"]-1):.0f}%', "rate_white / rate_black − 1")
put("per_callback_white", 100/F["rate_white"]["value"], f'{100/F["rate_white"]["value"]:.0f}', "1 / rate_white")
put("per_callback_black", 100/F["rate_black"]["value"], f'{100/F["rate_black"]["value"]:.0f}', "1 / rate_black")
z, p = proportions_ztest([kw, kb], [mw, mb])
put("p_gap", p, "p < 0.001" if p < .001 else f"p = {p:.3f}", f"two-sided two-proportion z-test, z = {z:.2f}")
for b, lab in ((0, "white"), (1, "black")):
    for h, q in ((0, "low"), (1, "high")):
        rate(f"rate_{lab}_{q}", df[(df.black == b) & (df.high == h)], f"{lab}-sounding names, {q}-quality résumés")
    for c in ("boston", "chicago"):
        rate(f"rate_{lab}_{c}", df[(df.black == b) & (df.city == c)], f"{lab}-sounding names, {c}")
    d = F[f"rate_{lab}_high"]["value"] - F[f"rate_{lab}_low"]["value"]
    put(f"quality_gain_{lab}", d, f"{d:.1f}", f"rate_{lab}_high − rate_{lab}_low, percentage points")
for c in ("boston", "chicago"):
    d = F[f"rate_white_{c}"]["value"] - F[f"rate_black_{c}"]["value"]
    put(f"gap_{c}", d, f"{d:.1f}", f"rate_white_{c} − rate_black_{c}, percentage points")
specs = {"m1": "y ~ black", "m2": "y ~ black + high", "m3": "y ~ black * high", "m4": "y ~ black * high + female + boston + experience"}
for k, f in specs.items():
    r = smf.ols(f, df).fit(cov_type="HC1"); ci = r.conf_int()
    for t in r.params.index:
        key = f"{k}_{t.replace(':', 'x')}"
        put(key+"_b", 100*r.params[t], f"{100*r.params[t]:.1f}", f"OLS linear probability model {k}: {f}; coefficient ×100")
        put(key+"_se", 100*r.bse[t], f"{100*r.bse[t]:.1f}", f"HC1 robust standard error ×100, model {k}")
        put(key+"_lo", 100*ci.loc[t, 0], f"{100*ci.loc[t, 0]:.1f}", f"95% CI lower bound, model {k}")
        put(key+"_hi", 100*ci.loc[t, 1], f"{100*ci.loc[t, 1]:.1f}", f"95% CI upper bound, model {k}")
json.dump(F, open(H / "facts.json", "w"), indent=1, ensure_ascii=False)
print(len(F), "facts;", {k: F[k]["text"] for k in ("rate_white_boston", "rate_black_boston", "rate_white_chicago", "rate_black_chicago", "gap_boston", "gap_chicago", "p_gap")})
