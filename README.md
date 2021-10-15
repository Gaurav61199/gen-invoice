# gen-invoice
This is a program based on python/pandas to generate invoice data and track Purchase Order records

There are three input files 
1. containing logistic CN detail and UOM
2. UOM description and rates
3. Purchase order detail associated with the UOM

python script depending upon the UOM details in #1 file automatically assigns it PO and calculates the invoice amount for a particular UOM and also tracks PO and show the plot of PO status
