# ArcPy Feature Image Exporter

Export images from layouts in ArcGIS for Desktop as JPEGs or PNGs, one
per feature based on field selection in a single layer. A map document and its corresponding layout may be setup and unique features, based on a uniquely-valued field name, looped over for export. The extent of individual features may be used to fill the data frame for each image to be saved, with the scale used for each data frame dependent on the image, or the features may be scaled proportionally in the data frame. The extent may be scaled up to add padding within the data frame, useful when the feature is symbolized using with a line that would otherwise overflow the data frame. Image output size depends on DPI and the established page size (e.g., 300 DPI and a 16"x9" page size would produce images at 4800x2700 pixels).

This script is not intended to run outside of ArcGIS and is packaged with a toolbox.

## Parameters/Usage

* Feature layer
* Output directory
* Fill type
* Extent scaling
* Page size 
* DPI
* JPEG quality

## Map Document Setup

The map document may contain multiple data frames, but the feature layer used for feature/image selection must be in the first data frame. Setup the page size and layout the data frame(s) as appropriate.

## Examples

Demonstration map documents and sample data are provided in `demo/`.

### Demo 1: Minnesota counties

### Demo 2: Labeled points

### Demo 3: Multiple data frames


## Compatibility
ArcGIS for Desktop 10.3.1. Other versions are untested. No extensions are required.

## Known Issues
* Clipping the data frame to a shape produces errors which require restarting ArcGIS for Desktop.
* Filename uniqueness support is not fully functional

