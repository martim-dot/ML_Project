# In-Depth Missing Values Analysis

#Real-world aviation records frequently suffer from incomplete reporting[cite: 3]. In this section, we investigate missing data across four dimensions:
#1. **Explicit missing values (`NaN`)** in both `learn.csv` and `predict.csv` (to ensure our future preprocessing pipeline handles test-set gaps safely).
#2. **Disguised categorical missing labels** (such as `UNK`, `Unk`, and `NR`).
#3. **Impossible values** acting as placeholders for unrecorded measurements (e.g., `0` or `33333`).
#4. **Missingness informativeness**, checking whether missing entries correlate with the target variable (`fatal`).

# 1. Explicit missing values (learn vs predict)
X_learn = learn.drop(columns=["fatal"])

missing_df = pd.DataFrame({
    "learn_%": X_learn.isna().mean() * 100,
    "predict_%": predict.isna().mean() * 100
}).round(2)
missing_df = missing_df[(missing_df["learn_%"] > 0) | (missing_df["predict_%"] > 0)].sort_values("learn_%", ascending=False)

display(missing_df.T)

ax = missing_df.plot(kind="bar", figsize=(12, 4), color=["#7aa6c2", "#e07a5f"], width=0.8)
ax.set_title("Percentage of Explicit Missing Values (learn.csv vs. predict.csv)")
ax.set_ylabel("% missing")
plt.xticks(rotation=75)
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()


# 2. Disguised missing values in categorical columns
cat_cols = X_learn.select_dtypes(exclude="number").columns
tokens = {"UNK", "Unk", "NR"}

disguised = []
for col in cat_cols:
    n_nan = X_learn[col].isna().sum()
    n_unk = X_learn[col].isin(tokens).sum()
    if n_nan + n_unk > 0:
        disguised.append({
            "column": col,
            "NaN_%": round(n_nan / len(X_learn) * 100, 2),
            "UNK/NR_%": round(n_unk / len(X_learn) * 100, 2),
            "total_missing_%": round((n_nan + n_unk) / len(X_learn) * 100, 2)
        })

display(pd.DataFrame(disguised).sort_values("total_missing_%", ascending=False))




# 3. Impossible values acting as missing
imp = pd.Series({
    "sky_ceil_ht == 0": (learn["sky_ceil_ht"] == 0).mean() * 100,
    "gust_kts == 0": (learn["gust_kts"] == 0).mean() * 100,
    "wind_dir_deg == 0": (learn["wind_dir_deg"] == 0).mean() * 100,
    "eng_power == 0": (learn["eng_power"] == 0).mean() * 100,
    "altimeter == 0 or < 25 or > 35": ((learn["altimeter"] == 0) | (learn["altimeter"] < 25) | (learn["altimeter"] > 35)).mean() * 100,
    "acft_year == 0 or > 2023": ((learn["acft_year"] == 0) | (learn["acft_year"] > 2023)).mean() * 100,
    "total_seats == 0 or > 600": ((learn["total_seats"] == 0) | (learn["total_seats"] > 600)).mean() * 100,
    "pilot_age < 14 or > 100": ((learn["pilot_age"] < 14) | (learn["pilot_age"] > 100)).mean() * 100,
    "apt_elev == 33333 or > 15000": ((learn["apt_elev"] == 33333) | (learn["apt_elev"] > 15000)).mean() * 100,
    "wx_temp < -80 or > 140": ((learn["wx_temp"] < -80) | (learn["wx_temp"] > 140)).mean() * 100,
}).round(2).sort_values(ascending=False).to_frame("% of rows")

display(imp)


# 4. Fatal rate when value is missing vs. present
rows = []
for col in missing_df.index:
    is_na = learn[col].isna()
    rows.append({
        "column": col,
        "% missing": round(is_na.mean() * 100, 1),
        "fatal_rate | missing": round(learn.loc[is_na, "fatal"].mean(), 3),
        "fatal_rate | present": round(learn.loc[~is_na, "fatal"].mean(), 3),
    })

display(pd.DataFrame(rows))