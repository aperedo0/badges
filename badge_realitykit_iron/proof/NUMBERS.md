# Smoothness measurements

Display Rec.709 luma levels on the 0–255 8-bit proof image. Broad facet masks exclude the pre-rule polished bevel assignments.

| Render | Mean facet residual | Mean facet grain | Ring grain | Ring mottle | Inset L grain | Inset R grain |
|---|---:|---:|---:|---:|---:|---:|
| iron_stage, pose 0 | 0.281 | 0.232 | 2.337 | 3.441 | 0.149 | 0.145 |
| iron_harsh, pose 0 | 0.291 | 0.218 | 2.369 | 3.792 | 0.194 | 0.162 |
| iron_stage, pose 20 | 0.538 | 0.245 | 1.484 | 2.430 | 0.134 | 0.187 |
| iron_harsh, pose 20 | 0.574 | 0.246 | 1.471 | 2.344 | 0.206 | 0.429 |
| iron_harsh, pose 45 | 0.457 | 0.316 | 1.695 | N/A | 0.169 | 0.741 |
| silver_stage, pose 0 | 0.915 | 0.306 | 2.008 | 2.639 | 0.390 | 0.359 |
| silver_harsh, pose 0 | 0.998 | 0.316 | 2.126 | 2.794 | 0.471 | 0.429 |
| silver_stage, pose 20 | 0.487 | 0.279 | 2.092 | 3.366 | 0.360 | 0.405 |
| silver_harsh, pose 20 | 0.508 | 0.274 | 2.111 | 3.072 | 0.337 | 0.482 |
| iron_raw, pose 0 | 2.092 | 2.011 | 2.504 | 3.732 | 0.273 | 0.270 |
| iron_realtime, pose 0 | 0.222 | 0.189 | 2.173 | 3.680 | 0.196 | 0.168 |

N/A: too few pixels survive the supplied mask erosion at 45 degrees. Ring metrics include physical curvature/highlight variation. The raw Cycles proof retains Monte Carlo indirect noise; the real-time proof uses Eevee with denoising and ray-traced indirect bounces disabled. Full per-facet, edge and patch values are in the corresponding JSON/TXT files. See REPORT.md for interpretation and limitations.