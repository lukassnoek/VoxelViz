# VoxelViz
Visualization tool for fMRI data-sets using Plotly Dash. Submitted to the TransIP VPS competition.

### Features
The tool is just a prototype right now, but it has the following features.

#### Show different datasets/results
For example, I loaded in results from two different analyses (here: "Copes"):

![alt text](https://github.com/lukassnoek/VoxelViz/raw/master/different_datasets.gif "Logo Title Text 1")

#### Adjust the (statistical) threshold for MRI images
Usually, results from (f)MRI analyses are thresholded. This can be done dynamically with VoxelViz:

![alt text](https://github.com/lukassnoek/VoxelViz/raw/master/threshold.gif "Logo Title Text 1")

#### Scrolling
The brain is of course a 3D dimensional object that is, here, visualized in 2D. The scrolling
options allows you to pick a dimension ("X", "Y", "Z") and scroll through it:

![alt text](https://github.com/lukassnoek/VoxelViz/raw/master/scrolling.gif "Logo Title Text 1")

### ToDo
Couple of thing that I'd still like to implement (before the deadline of 8 August):

- Add a timeseries plot corresponding to the "hoover" of the brain-plot
- Fix styling (rows, columns)
- Add some extra text (explanation)

### Trying out yourself
You could try this yourself (but no guarantees that it works on your computer) by
cloning/downloading this repo and running `python app.py`. This app needs the
following Python packages:

- `dash` and `dash`-derivatives (see Dash website)
- `nibabel`
- `numpy`
- `plotly`