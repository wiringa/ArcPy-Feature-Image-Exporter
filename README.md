# ArcPy Feature Image Exporter

Export images from layouts in ArcGIS for Desktop as JPEGs or PNGs, one
per feature based on a unique field in a single layer. Single layer uniqueness supported, but may be used with multiple layers and data frames.

This script is not intended to run outside of ArcGIS and is packaged with a toolbox.

## Parameters/Usage

* __Input layer__ contains the individual features to export images around
* __Unique field__ is a text field within __Input layer__ that contains unique values for each feature. These values will be used for output filenames.
* __Output directory__ is the location where images will be stored.
* __Fill type__ determines how each feature fills the data frame when exported. If set to `fill`, each feature will be scaled to use the largest width and height possible within the data frame, subject to the value of __Extent scaling__; output images will have the same dimensions but the data frame containing the features may vary in scale. Use the `proportional` setting to calculate the smallest scale across all features, subject to __Extent scaling__, and apply that scale across all exported images. Default: `fill`
* __Extent scaling__ is the percentage each extent is scaled within the data frame. A value of more than 100 scales up the dimensions of the extent, having the effect of reducing the feature size (smaller scale output). This is useful when padding within images is desirable, especially if line symbolization overflows the data frame and image when set to 100. Default: `100`
* __DPI__ is the standard dots per inch to use when exporting. Multiply DPI times the height and width of the page size to get the output image size, (e.g., 72DPI on a 16"x9" will produce an 1152x648 image). Default: `96`
* __Image type__ is one of `PNG` or `JPEG`. Default: `PNG`
* __JPEG quality__ is set between `0` and `100` when __Image type__ is `JPEG`. Default value in `60`, common for save-for-web situations.

## General Process for Use

1. Create a new map document.
1. Set an appropriate page size, with the same aspect ratio that your final images will have. Whole numbers make for easy arithmetic.
1. Add data to one or more data frames. Ensure the features you will export images based on are contained in the first data frame.
1. As the tool only supports text features with unique names, if the desired field is numeric, add a text field and calculate strings into the new field.
1. If the data includes separate features with the same name, dissolve into multipart features (or find another way to uniquely name things).
1. Establish page layout.
1. Run the tool, setting tool parameters as appropriate. Watch for extent scaling and fill type, in particular.

The `arcpy.env.overwriteOutput` environment variable is honored.

## Map Document Setup

The map document may contain multiple data frames, but the feature layer used for feature/image selection must be in the first data frame. Setup the page size and layout the data frame(s) as appropriate.

## Examples
Demonstration map documents and sample data are provided in `demo/`.

### Demo 1: Minnesota counties
Minnesota's 87 counties are dissolved into multipart features and labeled with county name and FIPS code (parenthetically). Page size is set to 10"x10". Run the tool using the only layer provided&mdash;`mn_county_boundaries_dissolved`&mdash; and `CTY_NAME` as the unique field. This will produce 87 images, named by county, with dimensions ten times the provided DPI.

### Demo 2: Interstates in Minnesota
Interstate highways in Minnesota have been dissolved into multipart lines by route number. Use the `InterstatesMN` layer and the `ROUTE_NUMBER` field to generate ten images.

### Demo 3: Multiple data frames
Demo two repeated, with an additional data frame at a fixed scale showing the entire state, with the variable frame to the right of the images.

### Demo Data Sources
* Minnesota Department of Natural Resources, [County Boundaries, Minnesota](https://gisdata.mn.gov/dataset/bdry-counties-in-minnesota)
* Minnesota Department of Transportation, [Roads, Minnesota, 2012](https://gisdata.mn.gov/dataset/trans-roads-mndot-tis)

## Compatibility
ArcGIS for Desktop 10.3.1. Other versions are untested. No extensions required.

## Known Issues and Limitations
* Only unique fields of type text are supported.
* Clipping the data frame to a shape produces errors which require restarting ArcGIS for Desktop.
* Filename uniqueness support is not fully functional. If `arcpy.env.overwriteOutput=True`, files may be overwritten. If `False`, warnings will be produced in the case of non-unique filenames (or, if files of the same name already exist).

