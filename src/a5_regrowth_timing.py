# -------------------------------------------------------------------------
# IMPORT PACKAGES
# -------------------------------------------------------------------------
# Packages
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde


# -------------------------------------------------------------------------
# YYREGR DISTRIBUTION PER MAP (SUPPLEMENTARY)
# -------------------------------------------------------------------------
# Read ages, convert ha to mha
potapov_yyregr = pd.read_csv("data/map/areaha_potapov_age.csv") \
    .set_index(pd.Index(range(20, -1, -1)))["area"] / 1e6
zhang_yyregr = pd.read_csv("data/map/areaha_zhang_age.csv") \
    .set_index(pd.Index(range(20, -1, -1)))["area"] / 1e6
mapbiomas_yyregr = pd.read_csv("data/map/areaha_mapbiomas_age.csv") \
    .set_index(pd.Index(range(20, -1, -1)))["area"] / 1e6

# Adjust potapov to annual increments
potapov_yyregr = potapov_yyregr.groupby(pd.cut(potapov_yyregr.index, 
    bins=[-1, 4, 9, 14, 20], labels=["0-4", "5-9", "10-14", "15-20"]), 
    observed=True).transform("mean")

# Convert age to regrowth year
potapov_yyregr.index = 2020 - potapov_yyregr.index
zhang_yyregr.index = 2020 - zhang_yyregr.index
mapbiomas_yyregr.index = 2020 - mapbiomas_yyregr.index

# Remove year 2000
potapov_yyregr = potapov_yyregr[1:]
zhang_yyregr = zhang_yyregr[1:]
mapbiomas_yyregr = mapbiomas_yyregr[1:]

# Initialize figure
fig, ax = plt.subplots(figsize=(10, 6))

# Add zhang data
ax.fill_between(zhang_yyregr.index.values, zhang_yyregr.values, 0, 
    color="#C46A97", alpha=0.8, label="GLC_FCS30D")
ax.plot(zhang_yyregr.index.values, zhang_yyregr.values, color="#882255", 
    linewidth=0, alpha=0.9, marker="o", markersize=7, markerfacecolor = "#882255", 
    markeredgecolor="white", markeredgewidth=0.5)

# Add mapbiomas data
ax.fill_between(mapbiomas_yyregr.index.values, mapbiomas_yyregr.values, 0, 
    color="#C6C670", alpha=0.6, label="MapBiomas")
ax.plot(mapbiomas_yyregr.index.values, mapbiomas_yyregr.values, color="#999933", 
    linewidth=0, alpha=0.9, marker="o", markersize=7, markerfacecolor = "#999933", 
    markeredgecolor="white", markeredgewidth=0.5)

# Add potapov data
ax.fill_between(potapov_yyregr.index.values, potapov_yyregr.values, 0, 
    color="#88CCEE", alpha=0.6, label="GLAD LC")
ax.plot(potapov_yyregr.index.values, potapov_yyregr.values, linestyle='none', 
    marker="o", markersize=7, markerfacecolor = "#88CCEE", 
    markeredgecolor="#323030", markeredgewidth=0.5)

# Adjust axes labels
ax.set_xlabel("Regrowth Year")
ax.set_ylabel("Area (Mha)")

# Remove spines
sns.despine(left=True, bottom=True)

# Adjust axis tickmarks
ax.set_xticks(sorted(mapbiomas_yyregr.index.values))
ax.set_xticklabels(sorted(mapbiomas_yyregr.index.values))

# Add legend and gridlines
ax.legend()
ax.grid(axis="both", linestyle="--", alpha=0.3)

# Save plot
plt.tight_layout()
plt.savefig("data/figures/supplementary/map_yyregr.png", dpi=300, bbox_inches='tight')
print('figure saved to data/figures/supplementary/map_yyregr.png')
plt.close(fig)


# -------------------------------------------------------------------------
# COMPARE REFERENCE AND MAP REGROWTH YEARS
# -------------------------------------------------------------------------
# Read sample data
sampledata = pd.read_csv('data/samples/fd30ref_SA_labels.csv')

# Define function to output shared regrowth samples
def sharedsamples(df, col2):

    # Ensure columns are set to integer
    df['YYregr'] = df['YYregr'].astype('Int16')
    df[col2] = df[col2].astype('Int16')

    # Filter for shared valid regrowth years
    shared = df[(df['YYregr'] > 2000) & (df[col2] > 2000) & (df[col2].notna())]

    # Calculate difference
    shared['diff'] = shared['YYregr'] - shared[col2]

    # Calculate age
    shared['age'] = 2020 - shared['YYregr']

    return shared[['FID', 'traj','YYregr', col2, 'diff', 'age']].copy()

# Filter for shared regrowth years
shared_zhang = sharedsamples(sampledata, 'glcYYregr')
shared_potapov = sharedsamples(sampledata, 'gladYYregr')
shared_mapbiomas = sharedsamples(sampledata, 'mbYYregr')

# Filter for forest interpretations
shared_zhang_f = shared_zhang[shared_zhang['traj'].isin(
    ['Secondary Forest', 'Afforested Land'])]
shared_potapov_f = shared_potapov[shared_potapov['traj'].isin(
    ['Secondary Forest', 'Afforested Land'])]
shared_mapbiomas_f = shared_mapbiomas[shared_mapbiomas['traj'].isin(
    ['Secondary Forest', 'Afforested Land'])]


# -------------------------------------------------------------------------
# DIFFERENCE IN REGROWTH YEAR (ALL YYREGR, MAIN)
# -------------------------------------------------------------------------
# Initialize figure
fig, ax = plt.subplots(figsize=(10, 6))

# Add data (incl. degradation + forest plantations)
sns.kdeplot(data=shared_zhang['diff'], color="#882255", linewidth=2.5, 
    label=f'GLC_FCS30D (n={len(shared_zhang)})', ax=ax)
sns.kdeplot(data=shared_potapov['diff'], color="#88CCEE", linewidth=2.5, 
    label=f'GLAD LC (n={len(shared_potapov)})', ax=ax)
sns.kdeplot(data=shared_mapbiomas['diff'], color="#999933", linewidth=2.5, 
    label=f'MapBiomas (n={len(shared_mapbiomas)})', ax=ax)

# Remove box/spines
sns.despine(left=True, bottom=True)

# Add gridlines
ax.grid(True, axis='y', alpha=0.7, linestyle='--', linewidth=0.8)
ax.axvline(x=0, color='gray', linewidth=1.5, linestyle='--', alpha=0.7)

# Add legend
ax.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, -0.15),
           ncols=3, frameon=True)

# Add labels
ax.set_xlabel('Difference in Regrowth Years (Reference-Map)', fontsize=14)
ax.set_ylabel('Density', fontsize=14)

# Helper: find the x location of each KDE's peak, to place text nearby
def kde_peak(data):
    kde = gaussian_kde(data)
    xs = np.linspace(data.min(), data.max(), 500)
    ys = kde(xs)
    peak_x = xs[np.argmax(ys)]
    peak_y = ys.max()
    return peak_x, peak_y

datasets = [
    (shared_zhang['diff'], "#882255", 'GLC_FCS30D', 5, -0.26),
    (shared_potapov['diff'], "#88CCEE", 'GLAD LC', -5, -0.25),
    (shared_mapbiomas['diff'], "#999933", 'MapBiomas', 3.8, -0.05)
]

# Annotate mean/std near each peak, with manual offsets to avoid overlap
for data, color, name, x_offset, y_offset in datasets:
    mean, std = data.mean(), data.std()
    peak_x, peak_y = kde_peak(data)
    ax.text(peak_x + x_offset, peak_y * (1 + y_offset), f'μ={mean:.2f}\nσ={std:.2f}',
        color=color, fontsize=9, ha='center', va='bottom', fontweight='bold')

# Plot and save
plt.tight_layout()
plt.savefig('data/figures/main/yyregr_differences.png', dpi=300, bbox_inches='tight')
print('figure saved to data/figures/main/yyregr_differences.png')
plt.close(fig)


# -------------------------------------------------------------------------
# DIFFERENCE IN REGROWTH YEAR (NAT YYREGR, SUPPLEMENTARY)
# -------------------------------------------------------------------------
# Initialize figure
plt.figure(figsize=(12, 6))

# Add data (only natural forest gain)
sns.kdeplot(data=shared_zhang_f['diff'], color="#882255", linewidth=2.5, 
    label=f'GLC_FCS30D (natural forest gains, n={len(shared_zhang_f)})')
sns.kdeplot(data=shared_potapov_f['diff'], color="#88CCEE", linewidth=2.5, 
    label=f'GLAD LC (natural forest gains, n={len(shared_potapov_f)})')
sns.kdeplot(data=shared_mapbiomas_f['diff'], color="#999933", linewidth=2.5, 
    label=f'MapBiomas (natural forest gains, n={len(shared_mapbiomas_f)})')

# Add data (incl. degradation + forest plantations)
sns.kdeplot(data=shared_zhang['diff'], color="#882255", linewidth=1.5, 
    label=f'GLC_FCS30D (any forest gains, n={len(shared_zhang)})', linestyle='--')
sns.kdeplot(data=shared_potapov['diff'], color="#88CCEE", linewidth=1.5, 
    label=f'GLAD LC (any forest gains, n={len(shared_potapov)})', linestyle='--')
sns.kdeplot(data=shared_mapbiomas['diff'], color="#999933", linewidth=1.5, 
    label=f'MapBiomas (any forest gains, n={len(shared_mapbiomas)})', linestyle='--')

# Remove box/spines
sns.despine(left=True, bottom=True)

# Add gridlines
plt.gca().grid(True, axis='y', alpha=0.7, linestyle='--', linewidth=0.8)
plt.axvline(x=0, color='gray', linewidth=1.5, linestyle='--', alpha=0.7)

# Add legend
plt.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, -0.15),
           ncols=3, frameon=True)

# Add labels
plt.xlabel('Difference in Regrowth Years (Reference-Map)', fontsize=14)
plt.ylabel('Density', fontsize=14)

# Compute means for each series
means_text = (
    f"Mean differences (natural forest gains):\n"
    f"GLC_FCS30D: {shared_zhang_f['diff'].mean():.2f}\n"
    f"GLAD LC: {shared_potapov_f['diff'].mean():.2f}\n"
    f"MapBiomas: {shared_mapbiomas_f['diff'].mean():.2f}\n\n"
    f"Mean differences (any forest gains):\n"
    f"GLC_FCS30D: {shared_zhang['diff'].mean():.2f}\n"
    f"GLAD LC: {shared_potapov['diff'].mean():.2f}\n"
    f"MapBiomas: {shared_mapbiomas['diff'].mean():.2f}"
)

# Add text box with means (upper right corner of the axes)
plt.gca().text(0.98, 0.97, means_text, transform=plt.gca().transAxes,
    fontsize=9, va='top', ha='right',
    bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.8))

# Plot and save
plt.tight_layout()
plt.savefig('data/figures/supplementary/yyregr_differences_natplant.png', dpi=300, 
    bbox_inches='tight')
print('figure saved to data/figures/supplementary/yyregr_differences_natplant.png')
plt.close(fig)


# -------------------------------------------------------------------------
# REGROWTH ERROR AREAS (SUPPLEMENTARY)
# -------------------------------------------------------------------------
# Read strata area (s america)
sa_strataarea = pd.read_csv("data/map/areaha_strata.csv").iloc[:, 1:3]
sa_strataarea = sa_strataarea.set_index("class")["area"]
sa_mha = sa_strataarea.sum() / 1e6

# Define years and bar width
years = [2000, 2010, 2020]
x = np.arange(len(years))
width = 0.25

# Define function to read area estimates
def readarea(filename):

    # Read area estimates
    area = pd.read_csv(f"data/stehman/timing/{filename}_stats.csv")

    # Filter area estimation data
    area_prop = area[['class', 'area', 'se_a']].copy()

    # Split class and year
    area_prop['year'] = area_prop['class'].str.split('_').str[1].astype(int)
    area_prop['class'] = area_prop['class'].str.split('_').str[0]

    # Calculate 95% confidence interval
    area_prop['ci95'] = 1.96 * area_prop['se_a']

    # Create upper and lower limits
    area_prop['lower'] = area_prop['area'] - area_prop['ci95']
    area_prop['upper'] = area_prop['area'] + area_prop['ci95']

    # Copy and define columns of interest
    area_mha = area_prop.copy()
    cols = ['area', 'se_a', 'ci95', 'lower', 'upper'] 

    # Convert area and confidence intervals to mha
    for col in cols:
        area_mha[col] = area_mha[col] * sa_mha

    # Filter by class, fill missing years
    def by_class(cls):
        sub = area_mha[area_mha['class'] == cls].set_index('year')
        sub = sub.reindex(list(years))
        sub['class'] = cls
        sub[cols] = (sub[cols].fillna(0))
        return sub.reset_index()

    return by_class('Commission'), by_class('Omission'), by_class('Correct')

# Read stehman error areas
zhang_ce, zhang_oe, zhang_corr = readarea("ae_regrerrs_zhang")
potapov_ce, potapov_oe, potapov_corr = readarea("ae_regrerrs_potapov")
mapbiomas_ce, mapbiomas_oe, mapbiomas_corr = readarea("ae_regrerrs_mapbiomas")

# Define panels for plotting
panels = [
    ("GLC_FCS30D", zhang_ce,     zhang_oe,     zhang_corr),
    ("GLAD LC",    potapov_ce,   potapov_oe,   potapov_corr),
    ("MapBiomas",  mapbiomas_ce, mapbiomas_oe, mapbiomas_corr),
]

# Define colors for plotting
classes = [("Commission Error", -width, "#882255"),
           ("Omission Error", 0, "#88CCEE"),
           ("Correct", width, "#999933")]

# Initialize subfigures
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)

# Iterate over each dataset/panel
for ax, (title, *dfs) in zip(axes, panels):
    for (label, offset, color), df in zip(classes, dfs):

        # Plot data
        ax.bar(x + offset, df["area"], width,
               yerr=[np.minimum(df["ci95"], df["area"]), df["ci95"]],
               capsize=3, label=label, color=color)

    # Adjust tick labels
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_xlabel("Year")

    # Add title
    ax.set_title(title)

    # Add gridlines
    ax.grid(axis="y", alpha=0.3, linestyle="--") 
    ax.set_axisbelow(True)        

# Add y axis label and legend
axes[0].set_ylabel("Area (Mha)")
axes[2].legend()

# Save plot
plt.tight_layout()
plt.savefig('data/figures/supplementary/yyregr_errarea.png', dpi=300, 
            bbox_inches='tight')
print('figure saved to data/figures/supplementary/yyregr_errarea.png')
plt.close(fig)
