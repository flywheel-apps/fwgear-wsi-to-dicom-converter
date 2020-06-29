# fwgear-wsi-to-dicom-converter
Flywheel Gear implementation of GCP's conversion tool for converting whole slide images to DICOM

''' bash
docker build -t flywheel/fwgear-wsi-to-dicom-converter:0.1.0_1.0.3 .
wget http://openslide.cs.cmu.edu/download/openslide-testdata/Aperio/JP2K-33003-1.svs
wsi2dcm --input JP2K-33003-1.svs --outFolder ./dicoms --seriesDescription JP2K-33003-1
'''
