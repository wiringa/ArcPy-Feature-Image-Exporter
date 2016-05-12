import arcpy
import os.path
import sys

inputLayer = arcpy.GetParameterAsText(0)  # need text string, not object
uniqueField = arcpy.GetParameterAsText(1)  # handled
outputDir = arcpy.GetParameterAsText(2)  # handled
outputFillType = arcpy.GetParameterAsText(3)
extentScale = float(arcpy.GetParameter(4))  # expand/contract extent
outputDPI = arcpy.GetParameter(5)  # handled
outputFormat = arcpy.GetParameter(6)  # handled
outputJpegQual = arcpy.GetParameter(7)


def exportImage(imageType, mapDoc, outputDir, filename, res, jpegQuality=60):
    """Export image from page layout. Supports PNG and JPEG formats with
    adjustable resolution and JPEG quality (when applicable). Honors
    arcpy.env.overwriteOutput and warns when files are skipped.
    """
    if imageType == 'PNG':
        outAbsolute = outputDir + '\\' + f['uq'] + '.png'
        if os.path.isfile(outAbsolute) and not arcpy.env.overwriteOutput:
            arcpy.AddWarning('Outfile image for "' + f['uq'] +
                             '" already exists and will not be overwritten')
        else:
            arcpy.mapping.ExportToPNG(
                map_document=mxd,
                out_png=outAbsolute,
                data_frame='PAGE_LAYOUT',
                resolution=outputDPI
            )
    elif imageType == 'JPEG':
        outAbsolute = outputDir + '\\' + f['uq'] + '.jpg'
        if os.path.isfile(outAbsolute) and not arcpy.env.overwriteOutput:
            arcpy.AddWarning('Outfile image for "' + f['uq'] +
                             '" already exists and will not be overwritten')
        else:
            arcpy.mapping.ExportToJPEG(
                map_document=mxd,
                out_jpeg=outAbsolute,
                data_frame='PAGE_LAYOUT',
                resolution=outputDPI,
                jpeg_quality=jpegQuality
            )
    else:
        # This case shouldn't occur as validation is handled in the toolbox
        arcpy.AddError("Invalid image type for export: " + str(imageType))
        resetWorkspace(inputLayer, df, initialDefQuery, initialMapExtent)
        sys.exit()


def saferFilename(filename):
    """ Strip filenames of bad characters. Supposedly support Unicode
    characters, but untested here.
    http://stackoverflow.com/a/7406369
    """
    keepcharacters = (' ', '.', '_')
    return "".join(c for c in filename if c.isalnum() or
                   c in keepcharacters).rstrip()


def resetWorkspace(layer, dataFrame, defQuery, initExtent):
    """Reset the definition query and extent to their initial settings
    """
    arcpy.mapping.Layer(layer).definitionQuery = defQuery
    dataFrame.extent = initExtent
    arcpy.RefreshActiveView()

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]  # First data frame expected
if len(arcpy.mapping.ListDataFrames(mxd)) > 1:
    arcpy.AddMessage('More than one data frame exists. Your mileage may vary.')

# Store the initial extent and definition query to use later when resetting
# the workspace.
initialMapExtent = df.extent
initialDefQuery = (arcpy.mapping.Layer(inputLayer).definitionQuery).strip()

# Setup existing definition query string for use with per-feature
# queries. Appends " AND " to a non-empty initial definition query.
if initialDefQuery != '':
    arcpy.AddMessage('A definition query is already set for the selected ' +
                     'layer. Unique values will be AND\'d to the existing' +
                     ' query. Original definition query: ' + "\n" +
                     initialDefQuery)
    defQueryPrefix = initialDefQuery + ' AND '
else:
    defQueryPrefix = ''

# Determine the name of the shape-containing field in the feature layer and
# setup an empty list to hold identified features. Populate the list with
# the unique features, including their name, filename part, and extent.
shapeName = arcpy.Describe(inputLayer).shapeFieldName
exportFeatures = []
with arcpy.da.SearchCursor(inputLayer, [shapeName + '@', uniqueField]) as cursor:
    for row in cursor:
        # print '1'
        extent = row[0].extent
        exportFeatures.append({
            "uq": str(row[1]),
            "uqFilename": saferFilename(str(row[1])),
            "XMin": extent.XMin,
            "XMax": extent.XMax,
            "YMin": extent.YMin,
            "YMax": extent.YMax,
            })

# The script won't work correctly if the supposedly-unique field
# selected by the user doesn't contain unique values. Get values
# for names and filename parts into lists, then check those
# to ensure uniqueness of names.
maybeUniqueValues = [feature['uq'] for feature in exportFeatures]
maybeUniqueFilenames = [feature['uqFilename'] for feature in exportFeatures]
if len(maybeUniqueValues) != len(set(maybeUniqueValues)):
    arcpy.AddError("Feature values are not unique")
    resetWorkspace(inputLayer, df, initialDefQuery, initialMapExtent)
    sys.exit()
else:
    arcpy.AddMessage("Processing " + str(len(maybeUniqueValues)) + " features")

if len(maybeUniqueFilenames) != len(set(maybeUniqueFilenames)):
    arcpy.AddError("Output filenames would not be unique")
    resetWorkspace(inputLayer, df, initialDefQuery, initialMapExtent)
    sys.exit()

# Loop over features to export. Calculate extent for each based on extent
# scale parameter. If proportional scaling is used, don't export the image.
# Instead, record the scales to determine the smallest scale to use when
# doing final exports. Export images in-loop if fill type is fill.
for key, f in enumerate(exportFeatures):
    print f["uq"]

    arcpy.mapping.Layer(inputLayer).definitionQuery = defQueryPrefix + "CTY_NAME = '" + f['uq'] + "'"

    exportFeatures[key]['featureExtentFill'] = arcpy.Extent(
        XMin=f['XMin'] - ((f['XMax'] - f['XMin']) * (extentScale / 100 - 1) / 2),
        XMax=f['XMax'] + ((f['XMax'] - f['XMin']) * (extentScale / 100 - 1) / 2),
        YMin=f['YMin'] - ((f['YMax'] - f['YMin']) * (extentScale / 100 - 1) / 2),
        YMax=f['YMax'] + ((f['YMax'] - f['YMin']) * (extentScale / 100 - 1) / 2),
    )

    df.extent = exportFeatures[key]['featureExtentFill']

    # If output fill type is "fill," images can be exported not.
    # If not (implies "proportional"), record the scale used for the current
    # feature.
    if outputFillType == 'fill':
        arcpy.RefreshActiveView()
        exportImage(outputFormat, mxd, outputDir, f['uqFilename'],
                    outputDPI, outputJpegQual)
    else:
        exportFeatures[key]['fillScale'] = df.scale

# If feature scaling is proportional, handle that case with another loop, with
# the smallest scale calculated prior to this. Export images here.
if outputFillType == 'proportional':
    # Get the smallest scale (highest number) used across all features
    outputScaleMin = max([feature['fillScale'] for feature in exportFeatures])
    arcpy.AddMessage("Exporting with fixed scale of 1:" + str(outputScaleMin))

    for key, f in enumerate(exportFeatures):
        arcpy.mapping.Layer(inputLayer).definitionQuery = defQueryPrefix + "CTY_NAME = '" + f['uq'] + "'"
        df.extent = exportFeatures[key]['featureExtentFill']
        df.scale = outputScaleMin
        exportImage(outputFormat, mxd, outputDir, f['uqFilename'],
                    outputDPI, outputJpegQual)

# Reset workspace elements that were adjusted
resetWorkspace(inputLayer, df, initialDefQuery, initialMapExtent)
