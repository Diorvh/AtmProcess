# Sample Data

The project includes 25 TIFF images in two small sample sets. They support GUI demonstration and regression checks, not a complete experimental dataset or an independently validated scientific reference.

## Experiment 29: GUI Demonstration

`atomization/实验编号29/` contains 20 frames, `8000.tif` through `8019.tif`, from the experiment recorded on 2023-04-15. They are the first 20 frames of the historical 8000-8500 processing interval, not the first frames of the Cine recording.

The Cine was exported as 12-bit color TIFF and converted to grayscale with this program. The bundled images are single-channel `uint16` TIFF files; no 8-bit intermediate was used. Export details, parameter provenance, file sizes and SHA-256 checksums are recorded in [source.json](atomization/实验编号29/source.json).

On first launch without a local `settings.json`, [settings.example.json](../settings.example.json) selects these images and loads the atomization parameters. Existing personal settings take precedence. This short sequence demonstrates the processing workflow; it is not a representative sample for experimental statistics.

## Experiment 55: Regression Checks

The five TIFF images under `atomization/实验编号55/` are retained for import, image-reading and multiprocessing checks.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `6800.tif` | 1061676 | `20bb0f04f6dce510153242aec7c4d1688bc10a87a6e29e9facc54be031461995` |
| `6801.tif` | 1063664 | `95c072aea863be85732adb199b5c62310bd15a3b09a414fb5f216ae231cd2524` |
| `6802.tif` | 1062918 | `cad80bad7f54ed64147906fd6d7e596b0107dfc0b6c2fe79290a219e268478b1` |
| `6803.tif` | 1062826 | `87c22557eab73b19180dd0b55c9966fa73b0c6df61a1995a811a4d85745df228` |
| `6804.tif` | 1064662 | `7a43e1f308b753d93c6adc7d47ea91359b62c04cbd6376503da878cbdd7aa3f9` |

The existing multiprocessing check uses frames 6800, 6802 and 6804 and compares parallel results with a serial calculation. That checks execution consistency; it does not establish agreement with independent measurements.

## Scope and Reuse

Before public distribution, the data owner needs to confirm acquisition conditions, calibration, permitted reuse and the relationship of each sample set to the paper. Experiment 29 has the provenance record linked above; equivalent acquisition details are not yet provided for experiment 55. No data license or publication permission is implied by this file. No ground-truth angles are currently provided.
