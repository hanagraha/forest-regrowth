# -------------------------------------------------------------------------
# IMPORT PACKAGES AND READ SAMPLES
# -------------------------------------------------------------------------
# Packages
import numpy as np
import pandas as pd
import geopandas as gpd

# Read samples
sampledata = gpd.read_file('data/samples/fd30ref_SA.shp')


# -------------------------------------------------------------------------
# RECLASSIFY TRAJECTORY LABELS
# -------------------------------------------------------------------------
# Helper function to avoid repetition across potapov/zhang/etc.
def trajmatch(df, map_col):

    # Extract trajectory and reference labels
    ref = df['traj']
    map  = df[map_col]

    conditions = [

        # Stable non-forest = stable non forest + MATCHED forest plantations + MATCHED degraded forest
        (ref == 'Stable Non-Forest') |
        ((ref == 'Forest Plantations') & (map == 'Stable Non-Forest')) |
        ((ref == 'Degraded Forest') & (map == 'Stable Non-Forest')),

        # Stable forest = stable forest + MATCHED degraded forest
        (ref == 'Stable Forest') |
        ((ref == 'Degraded Forest') & (map == 'Stable Forest')),

        # Forest loss = deforestation + MATCHED forest plantation + MATCHED degradation
        (ref == 'Deforested Land') |
        ((ref == 'Degraded Forest') & (map == 'Forest Loss')) |
        ((ref == 'Forest Plantations') & (map.isin(['Forest Loss', 'Stable Forest']))),

        # Forest gain = afforestation + secondary forest + MATCHED degradation + MATCHED forest plantation
        ref.isin(['Afforested Land', 'Secondary Forest']) |
        ((ref == 'Degraded Forest') & (map == 'Forest Gain')) |
        ((ref == 'Forest Plantations') & (map == 'Forest Gain')),
    ]

    choices = ['Stable Non-Forest', 'Stable Forest', 'Forest Loss', 'Forest Gain']

    return np.select(conditions, choices, default='Unmatched')

# Reclassify trajectories (stable forest / loss / gain / stable nonforest)
sampledata['ref_traj'] = np.where(sampledata['traj'].isin(
    ['Stable Forest', 'Degraded Forest']), 'Stable Forest',
    np.where(sampledata['traj'].isin(['Stable Non-Forest']), 'Stable Non-Forest',
    np.where(sampledata['traj'].isin(['Deforested Land', 'Forest Plantations']), 
    'Forest Loss', 'Forest Gain')))

# Match reference labels to zhang and potapov and mapbiomas
sampledata['ref_pottraj'] = trajmatch(sampledata, 'potapov')
sampledata['ref_zhangtraj'] = trajmatch(sampledata, 'zhang')
sampledata['ref_mbtraj'] = trajmatch(sampledata, 'mapbiomas')


# -------------------------------------------------------------------------
# BIN YEAR LABELS INTO 10 YEAR PERIODS
# -------------------------------------------------------------------------
# Define year bins
bins = [-1, 2000, 2010, 2020]
labs = bins[1:]

# Define (output_col, source_col) pairs to bin
yearcols = [
    ('distperiod',              'YYdist'),
    ('regrperiod',              'YYregr'),
    ('zhang_distperiod',        'glcYYdist'),
    ('potapov_distperiod',      'gladYYdist'),
    ('mapbiomas_distperiod',    'mbYYdist'),
    ('zhang_regrperiod',        'glcYYregr'),
    ('potapov_regrperiod',      'gladYYregr'),
    ('mapbiomas_regrperiod',    'mbYYregr')
]

# Bin reference years
for out_col, src_col in yearcols[:2]:

    # Redefine column name
    collab = f'{out_col}_sankey10'

    # Bin years (no year = 2000)
    sampledata[collab] = pd.cut(sampledata[src_col], bins=bins, 
        labels=labs, right=True).astype(str)

# Bin map reference and map years
for out_col, src_col in yearcols:

    # Bin years in column (with YY data)
    sampledata[out_col] = pd.cut(sampledata[src_col], bins=bins, 
        labels=labs, right=True).astype(str)

    # Replace with 0 where source year is under 2000
    sampledata[out_col] = np.where(sampledata[src_col] < 2000, '255', 
        pd.cut(sampledata[src_col], bins=bins, labels=labs, right=True).astype(str))


# -------------------------------------------------------------------------
# CREATE COMBINED LABELS
# -------------------------------------------------------------------------
# Define function to create combined labels
def combined_label(df, col1, col2):
    return [f'{df[col1].iloc[i]} - {df[col2].iloc[i]}' for i in range(len(df))]

# Combine period and trajectory
sampledata['traj_distperiod'] = combined_label(sampledata, 'traj', 'distperiod')
sampledata['traj_regrperiod'] = combined_label(sampledata, 'traj', 'regrperiod')
sampledata['traj_distregr10'] = [f'{sampledata["traj"].iloc[i]} - \
    {sampledata["distperiod_sankey10"].iloc[i]} - {sampledata["regrperiod_sankey10"].iloc[i]}' \
    for i in range(len(sampledata))]


# -------------------------------------------------------------------------
# IDENTIFY REGROWTH ERRORS
# -------------------------------------------------------------------------
# Define function to classify errors
def regr_errs(predcol, refcol):

    # Extract classifications
    pred = sampledata[predcol] == 'Forest Gain'
    ref = sampledata[refcol] == 'Forest Gain'

    # Identify correct, commission, and omission errors
    errs = np.select([pred & ref, pred & ~ref, ~pred & ref],
        ["Correct", "Commission", "Omission"], default="None")

    # Add regrowth period to errors
    errperiod = pd.Series(errs, index=sampledata.index) + "_" + sampledata['regrperiod_sankey10'].astype(str)
    
    return errperiod

# Identify errors
sampledata['zhang_errs'] = regr_errs('zhang', 'ref_mbtraj')
sampledata['potapov_errs'] = regr_errs('potapov', 'ref_mbtraj')
sampledata['mapbiomas_errs'] = regr_errs('mapbiomas', 'ref_mbtraj')

# Export
sampledata.to_csv("data/samples/fd30ref_SA_labels.csv", index=False)
print('sample labels exported to data/samples/fd30ref_SA_labels.csv')
