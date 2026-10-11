# Sample Data

The project includes 20 TIFF images from experiment 29 for GUI demonstration, not a complete experimental dataset or an independently validated scientific reference.

## Experiment 29: GUI Demonstration

`atomization/实验编号29/` contains 20 frames, `8000.tif` through `8019.tif`, from the experiment recorded on 2023-04-15. They are the first 20 frames of the historical 8000-8500 processing interval, not the first frames of the Cine recording.

The Cine was exported as 12-bit color TIFF and converted to grayscale with this program. The bundled images are single-channel `uint16` TIFF files; no 8-bit intermediate was used. Export details, parameter provenance, file sizes and SHA-256 checksums are recorded in [source.json](atomization/实验编号29/source.json).

On first launch without a local `settings.json`, [settings.example.json](../settings.example.json) selects these images and loads the atomization parameters. Existing personal settings take precedence. This short sequence demonstrates the processing workflow; it is not a representative sample for experimental statistics.

## Scope and Reuse

Before public distribution, the data owner needs to confirm acquisition conditions, calibration, permitted reuse and the relationship of this sample set to the paper. The provenance record is linked above. No data license or publication permission is implied by this file. No ground-truth angles are currently provided.
