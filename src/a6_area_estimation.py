# -------------------------------------------------------------------------
# IMPORT PACKAGES AND CHECK DIRECTORY
# -------------------------------------------------------------------------
# Packages
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors


# -------------------------------------------------------------------------
# DEFINE RELEVANT FUNCTIONS
# -------------------------------------------------------------------------
# Read strata area data (s america)
sa_strataarea = pd.read_csv("data/map/areaha_strata.csv").iloc[:, 1:3]
sa_strataarea = sa_strataarea.set_index("class")["area"]
sa_mha = sa_strataarea.sum() / 1e6

# Define function to read area estimates
def readarea(filename, jointlabel=False):

    # Read area estimates
    area = pd.read_csv(f"data/stehman/{filename}_stats.csv")

    # Remove rows with 0 or na
    area = area.loc[~area.drop(columns='class').apply(
        lambda row: row.isna() | (row == 0), axis=1).all(axis=1)]

    # Filter area estimation data
    area_prop = area[['class', 'area', 'se_a']].copy()

    # Calculate 95% confidence interval
    area_prop['ci95'] = 1.96 * area_prop['se_a']

    # Create upper and lower limits
    area_prop['lower'] = area_prop['area'] - area_prop['ci95']
    area_prop['upper'] = area_prop['area'] + area_prop['ci95']

    # Split joint label
    if jointlabel:

        # Get labels
        lab1 = jointlabel[0]
        lab2 = jointlabel[1]

        # Split labels to individual columns
        area_prop[lab1] = area_prop['class'].str.split(' - ').str[0].str.strip()
        area_prop[lab2] = area_prop['class'].str.split(' - ').str[1].str.strip()
        
    area_mha = area_prop.copy()

    # Convert area and confidence intervals to mha
    for col in ['area', 'se_a', 'ci95', 'lower', 'upper']:
        area_mha[col] = area_mha[col] * sa_mha

    return area_mha

# Define function to adapt labels for plotting
def newline(df, column):
    df[column] = df[column].str.replace(' ', '\n')
    return df

# Read trajectory area estimates
area_traj = readarea("trajectory/ae_traj")


# -------------------------------------------------------------------------
# PLOT AREA ESTIMATION (TRAJECTORY)
# -------------------------------------------------------------------------
# Sort by area ascending 
area_traj = area_traj.sort_values('area', ascending=True).reset_index(drop=True)

# Adapt labels for plotting
area_traj = newline(area_traj, 'class')

# Define error bars
yerr_lower = area_traj['area'] - area_traj['lower']
yerr_upper = area_traj['upper'] - area_traj['area']
yerr = np.vstack([yerr_lower, yerr_upper])

# Initialize figure
fig, ax = plt.subplots(figsize=(10, 6))

# Add data for plotting
ax.bar(area_traj['class'], area_traj['area'], yerr=yerr, 
    capsize=5, color = '#88CCEE', ecolor='#545454')

# Adjust ticks/labels
ax.set_ylabel('Trajectory Area (Mha)', fontsize = 17)
ax.tick_params(axis='x', rotation=0, labelsize=14)
ax.tick_params(axis='y', labelsize=14)

# Add gridlines
ax.yaxis.grid(linestyle='--', alpha=0.6, zorder=0)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)
    
# Tight layout and save
plt.tight_layout()
plt.savefig('data/figures/main/area_trajectories_all.png', dpi=300, 
            bbox_inches='tight')
print('figure saved to data/figures/main/area_trajectories_all.png')
plt.close(fig)


# -------------------------------------------------------------------------
# PLOT AREA ESTIMATION (CHANGE AREA)
# -------------------------------------------------------------------------
# Filter for changes
area_changetraj = area_traj[area_traj['class'].isin(['Secondary\nForest', 
    'Afforested\nLand', 'Forest\nPlantations', 'Deforested\nLand'])].copy()

# Define error bars
yerr_lower = area_changetraj['area'] - area_changetraj['lower']
yerr_upper = area_changetraj['upper'] - area_changetraj['area']
yerr = np.vstack([yerr_lower, yerr_upper])

# Initialize figure
fig, ax = plt.subplots(figsize=(10, 6))

# Add data for plotting
ax.bar(area_changetraj['class'], area_changetraj['area'], yerr=yerr, 
    capsize=5, color = '#88CCEE', ecolor='#545454')

# Adjust ticks/labels
ax.tick_params(axis='x', rotation=0, labelsize=14)
ax.set_ylabel('Trajectory Area (Mha)', fontsize = 17)
ax.tick_params(axis='y', labelsize=14)

# Add gridlines
ax.yaxis.grid(linestyle='--', alpha=0.6, zorder=0)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Tight layout and save
plt.tight_layout()
plt.savefig('data/figures/main/area_trajectories_change.png', dpi=300, 
            bbox_inches='tight')
print('figure saved to data/figures/main/area_trajectories_change.png')
plt.close(fig)


# -------------------------------------------------------------------------
# PROCESS TRANSITION LINKS FOR SANKEY
# -------------------------------------------------------------------------
# Define disturbance transitions
dist_transitions = {
    'Afforested Land':    ('NF', 'NF'),
    'Deforested Land':    ('F',  'NF'),
    'Degraded Forest':    ('F',  'DF'),
    'Forest Plantations': ('F',  'NF'),
    'Secondary Forest':   ('F',  'NF'),
    'Stable Forest':      ('TF',  'TF'),
    'Stable Non-Forest':  ('TNF', 'TNF'),
}

# Define regrowth transitions
regr_transitions = {
    'Afforested Land':    ('NF', 'AF'),
    'Deforested Land':    ('NF', 'NF'),
    'Degraded Forest':    ('DF', 'DF'),
    'Forest Plantations': ('NF', 'PF'),
    'Secondary Forest':   ('NF', 'SF'),
    'Stable Forest':      ('TF', 'TF'),
    'Stable Non-Forest':  ('TNF', 'TNF'),
}

# Define color palettes
STATE_COLORS = {'F':  '#44AA99', 'NF': '#DDCC77', 'AF': '#999933',
    'PF': '#CC6677', 'SF': '#88CCEE', 'TNF': '#DDCC77', 'TF': '#44AA99'}

# Define labels
STATE_LABELS = {'F':  'Forest', 'NF': 'Non-Forest', 'AF': 'Afforested Land',
    'PF': 'Forest Plantations', 'SF': 'Secondary Forest', 'TNF': 'Non-Forest', 'TF': 'Forest'}

# Define years
years = [2000, 2010, 2020]

# Read area data
distregr10 = readarea("timing/ae_trajdistregr10")[['area', 'class', 'se_a']]
distregr10['trajectory'] = distregr10['class'].str.split(' - ').str[0].str.strip()
distregr10['distperiod'] = distregr10['class'].str.split(' - ').str[1].str.strip()
distregr10['regrperiod'] = distregr10['class'].str.split(' - ').str[2].str.strip()

# Filter for regrowth
regr = distregr10[distregr10['trajectory'].isin(['Afforested Land', 'Secondary Forest'])].copy()
regr2010 = regr[regr['regrperiod'].isin(['2000', '2010'])].copy()
regr2020 = regr[regr['regrperiod']=='2020'].copy()

# Filter for loss
loss = distregr10[distregr10['trajectory'].isin(['Deforested Land'])].copy()
loss2010 = loss[loss['distperiod'].isin(['2000', '2010'])].copy()
loss2020 = loss[loss['distperiod']=='2020'].copy()

# Create transitions per period
for y in years:
    distregr10[y] = [
        dist_transitions[row["trajectory"]][0] if y < int(row["distperiod"])
        else dist_transitions[row["trajectory"]][1] if y < int(row["regrperiod"])
        else regr_transitions[row["trajectory"]][1]
        for _, row in distregr10.iterrows()
    ]

# Remove stable data
transitions10 = distregr10[~distregr10['trajectory'].isin(['Stable Forest', 
    'Stable Non-Forest', 'Degraded Forest'])].copy()

# Aggregate flows per year-pair
def combine_se(x):
    return np.sqrt((x**2).sum())

# Create sankey links
links10 = []
for y1, y2 in zip(years[:-1], years[1:]):
    tmp = (transitions10.groupby([y1, y2], as_index=False)
           .agg(value=('area', 'sum'), se=('se_a', combine_se))
           .rename(columns={y1: 'src', y2: 'tgt'}))
    tmp['y1'] = y1
    tmp['y2'] = y2
    links10.append(tmp)

links10 = pd.concat(links10, ignore_index=True)

# Per-year state totals
year_totals10 = {y: transitions10.groupby(y)['area'].sum().to_dict() for y in years}


# -------------------------------------------------------------------------
# PLOT SANKEY DIAGRAM (BLANK, AREA + SE LABELS ADDED MANUALLY)
# -------------------------------------------------------------------------
# Define setup
BAR_W    = 0.07
GAP      = 0.01
FONTSIZE = 14

# Define x positions
x_pos = {y: i / (len(years) - 1) * 0.82 + 0.05 for i, y in enumerate(years)}

# Initialize figure
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Draw stacked bars
bar_bottoms = {}
for y in years:
    totals = year_totals10[y]
    grand  = sum(totals.values())
    bottom = 0.05
    bar_bottoms[y] = {}
    for state, val in sorted(totals.items()):
        h = val / grand * 0.85
        bar_bottoms[y][state] = (bottom, bottom + h)
        rect = mpatches.FancyBboxPatch(
            (x_pos[y] - BAR_W / 2, bottom), BAR_W, h,
            boxstyle="square,pad=0", linewidth=0.5,
            edgecolor='white', facecolor=STATE_COLORS.get(state, '#aaaaaa')
        )
        ax.add_patch(rect)
        if h > 0.04:
            ax.text(x_pos[y], bottom + h / 2, f"{val:.2f}\nMha", ha='center', va='center', 
                    fontsize=10, color='white', fontweight='bold')
        bottom += h + GAP
    ax.text(x_pos[y], 0.01, str(y), ha='center', va='bottom',
            fontsize=FONTSIZE, fontweight='bold', color="#494545")

# Draw flows with Mha labels
src_used = {y: {s: 0.0 for s in year_totals10[y]} for y in years}
tgt_used = {y: {s: 0.0 for s in year_totals10[y]} for y in years}

for y1, y2 in zip(years[:-1], years[1:]):
    sub   = links10[(links10['y1'] == y1) & (links10['y2'] == y2)].copy()
    grand = sum(year_totals10[y1].values())

    for _, row in sub.iterrows():
        src, tgt, val = row['src'], row['tgt'], row['value']
        if src not in bar_bottoms[y1] or tgt not in bar_bottoms[y2]:
            continue

        frac = val / grand * 0.85

        sb, _ = bar_bottoms[y1][src]
        sy0   = sb + src_used[y1][src]
        sy1   = sy0 + frac
        src_used[y1][src] += frac

        tb, _ = bar_bottoms[y2][tgt]
        ty0   = tb + tgt_used[y2][tgt]
        ty1   = ty0 + frac
        tgt_used[y2][tgt] += frac

        x0 = x_pos[y1] + BAR_W / 2
        x1 = x_pos[y2] - BAR_W / 2

        # Add Bezier ribbon
        N   = 50
        t   = np.linspace(0, 1, N)
        top_y = (1-t)**3*sy1 + 3*(1-t)**2*t*sy1 + 3*(1-t)*t**2*ty1 + t**3*ty1
        bot_y = (1-t)**3*sy0 + 3*(1-t)**2*t*sy0 + 3*(1-t)*t**2*ty0 + t**3*ty0
        x_arr = np.concatenate([x0 + t*(x1-x0), x0 + t[::-1]*(x1-x0)])
        y_arr = np.concatenate([top_y, bot_y[::-1]])
        ax.fill(x_arr, y_arr, color=STATE_COLORS.get(src, '#aaaaaa'), alpha=0.35, linewidth=0)

# Tight layout and save
plt.tight_layout()
plt.savefig("data/figures/main/trajectory_sankey.png", dpi=300, bbox_inches='tight')
print('figure saved to data/figures/main/trajectory_sankey.png')
plt.close(fig)


# -------------------------------------------------------------------------
# PLOT STABLE CLASSES IN 2000 and 2020
# -------------------------------------------------------------------------
# Extract trajectory areas for 2000 and 2020
area2000 = distregr10.groupby(2000)['area'].sum()
area2020 = distregr10.groupby(2020)['area'].sum()

# Reclassify
area2000_bars = pd.Series({
    'Stable Forest': area2000['TF'],
    'Changed Forest': area2000['F'] + area2000['DF'],
    'Stable Non-Forest': area2000['TNF'],
    'Changed Non-Forest': area2000['NF'] + area2000['PF']
})
area2020_bars = pd.Series({
    'Stable Forest': area2020['TF'],
    'Changed Forest': area2020['AF'] + area2020['SF'] + area2020['DF'],
    'Stable Non-Forest': area2020['TNF'],
    'Changed Non-Forest': area2020['NF'] + area2020['PF']
})

# Combine into one dataframe
combined = pd.DataFrame({'2000': area2000_bars, '2020': area2020_bars}).T.fillna(0)

# Define formatting for figure
cols = ['#44AA99', '#44AA99', '#DDCC77', '#DDCC77']
hatches = [None, '//', None, '//']
labels = combined.columns.tolist()

# Define helper function for darkening colors
def darken(color, factor=0.6):
    r, g, b = mcolors.to_rgb(color)
    return (r * factor, g * factor, b * factor)

# Initialize figure
fig, ax = plt.subplots(figsize=(3, 8))

# Add data to plot
bottom = pd.Series(0, index=combined.index)
for col, color, hatch in zip(labels, cols, hatches):
    ax.bar(combined.index.astype(str), combined[col], bottom=bottom,
        color=color, hatch=hatch, edgecolor=darken(color), linewidth=0,
        label=col)
    bottom += combined[col]

# Add combined labels for green (forest) and blue (non-forest) groups
green_cols = ['Stable Forest', 'Changed Forest']
blue_cols  = ['Stable Non-Forest', 'Changed Non-Forest']

# Add change and stable area labels
for x_idx, year in enumerate(combined.index):
    green_total = combined.loc[year, green_cols].sum()
    blue_total  = combined.loc[year, blue_cols].sum()

    green_mid = green_total / 2
    blue_mid  = green_total + blue_total / 2

    ax.text(x_idx, green_mid, f"{green_total:.2f}\nMha", ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')
    ax.text(x_idx, blue_mid, f"{blue_total:.2f}\nMha", ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Remove tick marks and labels
ax.set_xticks([])
ax.set_yticks([])

# Tight layout and save
plt.tight_layout()
plt.savefig("data/figures/main/stable_classes.png", dpi=300, bbox_inches='tight')
print('figure saved to data/figures/main/stable_classes.png')
plt.close(fig)
