# fwgear-wsi-to-dicom-converter
Flywheel Gear implementation of GCP's conversion tool for converting whole slide images to DICOM

This gear packages the google WSI to DICOM tool.  This tool relies on [OpenSlide](https://openslide.org), which supports a variety of file formats.

For more detailed information on this tool, and access to sample data, see the [wsiToDcm github repository](https://github.com/GoogleCloudPlatform/wsi-to-dicom-converter)

The information you need to know to run this as a gear in flywheel is duplicated here:

## Supporred file formats:
Currently, this gear supports all file types readable by OpenSlide:
- Aperio (.svs, .tif)
- Hamamatsu (.vms, .vmu, .ndpi)
- Leica (.scn)
- MIRAX (.mrxs)
- Philips (.tiff)
- Sakura (.svslide)
- Trestle (.tif)
- Ventana (.bif, .tif)
- Generic tiled TIFF (.tif)

## Preprocessing
No preprocessing is required for this gear

## Outputs
This gear will generate a number of output dicom files dependent on the input settings.
The wsiToDcm script frequently returns non-zero codes, despite running successfully with
no error messages.  Because of this, the gear cannot rely on the return code to indicate
success or failure of the code.  Therefor, the creation of any number of output files
is considered a successful run.  Please carefully examine the output of this gear to
ensure that it did run successfully. 


## Complete set of parameters

### Inputs:

##### Input_file
Input wsi file, supported by openslide.
##### jsonFile
Dicom json file with additional tags https://www.dicomstandard.org/dicomweb/dicom-json-format/

### Config:

##### tileHeight
Tile height px.
##### tileWidth
Tile width px.
##### levels 
Number of levels to generate, levels == 0 means number of levels will be read from wsi file.
##### downsamples 
Size factor for each level  for each level, downsample is size factor for each level.

eg: if base level size is 100x100 and downsamples is (1, 2, 10) then
- level0 100x100
- level1 50x50
- level2 10x10
##### startOn
Level to start generation.
##### stopOn 
Level to stop generation.
##### sparse 
Use TILED_SPARSE frame organization, by default it's TILED_FULL http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.17.3.html
##### compression 
Compression, supported compressions: jpeg, jpeg2000, raw.
##### seriesDescription 
(0008,103E) [LO] SeriesDescription Dicom tag.
##### studyId
(0020,000D) [UI] StudyInstanceUID Dicom tag.
##### seriesId
(0020,000E) [UI] SeriesInstanceUID Dicom tag.
##### jsonFile
Dicom json file with additional tags https://www.dicomstandard.org/dicomweb/dicom-json-format/
##### batch
Maximum frames in one file, as limit is exceeded new files is started.

eg: 3 files will be generated if batch is 10 and 30 frames in level
##### threads
Threads to consume during execution.
##### debug
Print debug messages: dimensions of levels, size of frames.
##### dropFirstRowAndColumn
Drop first row and column of the source image in order to workaround bug https://github.com/openslide/openslide/issues/268

