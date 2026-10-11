# Sample Data

The project includes 20 TIFF images from experiment 29 for GUI demonstration, not a complete experimental dataset or an independently validated scientific reference.

## Experiment 29: GUI Demonstration

`atomization/实验编号29/` contains 20 frames, `8000.tif` through `8019.tif`, from the experiment recorded on 2023-04-15. They are the first 20 frames of the historical 8000-8500 processing interval, not the first frames of the Cine recording.

The Cine was exported as 12-bit color TIFF and converted to grayscale with this program. The bundled images are single-channel `uint16` TIFF files; no 8-bit intermediate was used. Export details, parameter provenance, file sizes and SHA-256 checksums are recorded in [source.json](atomization/实验编号29/source.json).

On first launch without a local `settings.json`, [settings.example.json](../settings.example.json) selects these images and loads the atomization parameters. Existing personal settings take precedence. This short sequence demonstrates the processing workflow; it is not a representative sample for experimental statistics.

## Demonstration Summary Workbook

`atomization_summary_template.xlsx` is based on `20230415喷注盘6-1-2高压雾化实验-5-数据总结.xlsx`, worksheet `测量数据`, experiment 29 (original Excel row 31). It retains the source header and units/flow-correction information, the condition fields and their formulas, and the atomization parameter/result layout. The `1pix` calibration item, image-note column, breakup-length section, other experimental records and unrelated sheets are omitted. Formula references are adjusted to the single retained record in row 30 and to the removed column; intervening experiment records are blank and scientific constants in the retained formulas are unchanged.

Historical angle results, process count and timing are blank. `RStartL` and `RStartR` are added beside their corresponding `NumAvg` fields with the sample's value of zero. The original image-range fields describe frames 21000–21520; the included demo actually processes 8000–8019, as noted separately in the workbook. The originally blank ambient-gas field is left blank rather than inferred.

First launch copies the template to `results/atomization_summary.xlsx` only when the result file does not already exist. Batch export updates the record identified by experiment number 29. It does not modify the bundled template or copy any other experiment's conditions into the demonstration.

## Scope and Reuse

Before public distribution, the data owner needs to confirm acquisition conditions, calibration, permitted reuse and the relationship of this sample set to the paper. The provenance record is linked above. No data license or publication permission is implied by this file. No ground-truth angles are currently provided.
