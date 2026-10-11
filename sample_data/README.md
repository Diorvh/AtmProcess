# Sample Data

The five TIFF images under `atomization/实验编号55/` are the sample frames supplied with this project. They are retained for import, image-reading and multiprocessing checks, not as a complete experimental dataset or an independently validated scientific reference.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `6800.tif` | 1061676 | `20bb0f04f6dce510153242aec7c4d1688bc10a87a6e29e9facc54be031461995` |
| `6801.tif` | 1063664 | `95c072aea863be85732adb199b5c62310bd15a3b09a414fb5f216ae231cd2524` |
| `6802.tif` | 1062918 | `cad80bad7f54ed64147906fd6d7e596b0107dfc0b6c2fe79290a219e268478b1` |
| `6803.tif` | 1062826 | `87c22557eab73b19180dd0b55c9966fa73b0c6df61a1995a811a4d85745df228` |
| `6804.tif` | 1064662 | `7a43e1f308b753d93c6adc7d47ea91359b62c04cbd6376503da878cbdd7aa3f9` |

The existing multiprocessing check uses frames 6800, 6802 and 6804 and compares parallel results with a serial calculation. That checks execution consistency; it does not establish agreement with independent measurements.

Before public distribution, the data owner needs to document acquisition conditions, calibration, permitted reuse and the relationship of these frames to the paper. No data license or publication permission is implied by this file. No ground-truth angles are currently provided.
