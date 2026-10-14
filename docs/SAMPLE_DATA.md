# Educational sample stock
80 rows from the Ford portion of Aditya Desai's “100,000 UK Used Car Data set”.
Original: https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes
Kaggle search metadata lists CC0/Public Domain. Confirm source metadata if changing distribution/use.
Downloaded subset mirror: https://github.com/harshitsharma141/Car_Price_Prediction/blob/main/ford.csv
Source blob: c787761a1bab5b82a82c15804c1437e986920f5e
Rows 2–81, retrieved 14 October 2026. No adverts, seller contacts, registrations or photographs bundled.
Changes: trim model names, add make Ford, multiply pound prices by 100, expose existing mileage/transmission/fuel/engine fields as approved facts.
These are historical dataset prices, not current valuations or live available stock. Source-row provenance is retained.
Available/reserved/sold states, archive flags, IDs, revisions and timestamps are fictional application fixtures, not facts from the source.
Load sample stock replaces the in-memory prototype stock and clears its related enquiry/task fixtures. It does not write to a live backend. Reload resets the prototype.

## Other sources checked
DVM-Car: UK specifications, advertisements and images; CC BY-NC 4.0/non-commercial educational use. Larger research option: https://deepvisualmarketing.github.io/
UCI Automobile: 205 historical records from the 1985 yearbook; CC BY 4.0; useful for analysis, less suitable for modern UK stock: https://archive.ics.uci.edu/dataset/10/automobile
DfT vehicle licensing CSVs: make/model registration statistics; no sale prices: https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files
No live Auto Trader adverts or images were scraped.
