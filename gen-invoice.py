import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

invno  =  str(sys.argv[1]) #'1'; ##UPDATENOTE - UPDATE invoice number
invyear = str(sys.argv[2]) #'xxxx-xx';


#This function returns 1 if PO is available and returns 0 if PO is not available
def CheckPOAvailibility(UOM_NO,PORecords,NO_OF_MTOC):

#checking which PO among all available needs to be used and which are not available
#UPDATENOTE:ADD below +(PORecords.loc[PORecords['UOM NO']==46,'PO_X_REMAINING'].values[0] for new PO
		if PORecords.loc[PORecords['UOM NO']==46,'PO_K160164_REMAINING'].values[0] >= NO_OF_MTOC : 
			
			if PORecords.loc[PORecords['UOM NO']==UOM_NO,'PO_K160164_REMAINING'].values[0] >= 1 :
				#added new column in PORecords for recording PO availibility usage of input file
				column_name = 'INV' + invno + '_' + invyear
				if column_name in PORecords.columns:
					PORecords[column_name] = PORecords[column_name]
				else:
					PORecords[column_name] = 0
				
				PORecords.loc[UOM_NO-1,column_name] = PORecords.loc[UOM_NO-1,column_name] + 1 #updating number of PO in column of current invoice
				PORecords.loc[46-1,column_name] = PORecords.loc[46-1,column_name] + NO_OF_MTOC #to update more than one collection IN INVOICE COLUMN
				PORecords.loc[UOM_NO-1,'PO_K160164_REMAINING'] = PORecords.loc[UOM_NO-1,'PO_K160164_REMAINING'] - 1
				PORecords.loc[46-1,'PO_K160164_REMAINING'] = PORecords.loc[46-1,'PO_K160164_REMAINING'] - NO_OF_MTOC #Updating more than one collection PO
				
				#returnning po and its serial number
				return ['K-160164',PORecords.loc[PORecords['UOM NO']==UOM_NO,'PO_K160164_SR_NO'].values[0]];
			
			elif PORecords.loc[PORecords['UOM NO']==UOM_NO,'PO_XXXXX_REMAINING'].values[0] >= 1 :  ##UPDATENOTE - UPDATE FOR NEW PO
				
				invincremented = int(invno) + 1
				
				column_name = 'INV' + str(invincremented) + '_' + invyear
				if column_name in PORecords.columns:
					PORecords[column_name] = PORecords[column_name]
				else:
					PORecords[column_name] = 0
				
				PORecords.loc[UOM_NO-1,column_name] = PORecords.loc[UOM_NO-1,column_name] + 1 #updating number of PO in column of current invoice
				PORecords.loc[46-1,column_name] = PORecords.loc[46-1,column_name] + NO_OF_MTOC #to update more than one collection IN INVOICE COLUMN
				PORecords.loc[UOM_NO-1,'PO_XXXXX_REMAINING'] = PORecords.loc[UOM_NO-1,'PO_XXXXX_REMAINING'] - 1
				PORecords.loc[46-1,'PO_XXXXX_REMAINING'] = PORecords.loc[46-1,'PO_XXXXX_REMAINING'] - NO_OF_MTOC #Updating more than one collection PO
				
				#returnning po and its serial number
				return ['XXXXX',PORecords.loc[PORecords['UOM NO']==UOM_NO,'PO_XXXXX_SR_NO'].values[0]];
			else:
				return ['PO N/A','PO N/A']
			##UPDATENOTE:  repeat ifelse block for new PO of more than one collection
		else:
			return ['MTOC PO N/A','MTOC PO N/A']
		



#reads input file containing LRs for which invoice is to be made
inputData = pd.read_excel('InputData.xlsx')

#reads standard file containing UOM and agreement rates corresponding to that rates
uomRates = pd.read_excel("UOMRates.xlsx")

#combines input file data with uom and rates based on UOM NO
result = pd.merge(inputData,uomRates,how = "left", on=["UOM NO","UOM NO"])

#reads files containing PO information
PORecords = pd.read_excel("PORecords.xlsx")

#added new indicator column PO availibility status in result dataframe
result['PO NO'] = ""
result['MTOC'] = result['MTOC'].fillna(0)
result['Extra Collection Additions'] = ""
result['CN DATE'] = result['CN DATE'].dt.strftime("%d/%m/%Y")
result['PO SR NO'] = 0

for index , row in result.iterrows():
	flag = CheckPOAvailibility(row['UOM NO'],PORecords,row['MTOC'])
	result.at[index,'PO NO'] = flag[0]
	result.at[index,'PO SR NO'] = flag[1]
	if row['MTOC'] > 0:
		result.at[index,'Extra Collection Additions'] = str(row['AMOUNT']) + '+ (' + str(row['MTOC']) + '* ' +  str(uomRates.loc[uomRates['UOM NO']==46,'AMOUNT'].values[0])  + ')' #populates MTOC amount dynamically from UOM rates
		result.at[index,'AMOUNT'] = row['AMOUNT'] + (row['MTOC'] * uomRates.loc[uomRates['UOM NO']==46,'AMOUNT'].values[0])  #updates amount after addition for MTOC charges
	

uptoInvoice = int(invno) + result['PO NO'].nunique() - 1; #this is needed in case of multiple invoice for multiple POs
updatePORecordsColName = 'INV' + invno + '-' + str(uptoInvoice) + '_' + invyear


if result['PO NO'].nunique() == 1:
	INVOICE_FILE_NAME = 'GT_SMRTIPL_BILLDATA_' + 'INV' + str(invno) + '_'+ invyear + '.xlsx'; 
else:
	INVOICE_FILE_NAME = 'GT_SMRTIPL_BILLDATA_' + 'INV' + str(invno) + '_TO_' + str(uptoInvoice)  + '_'+ invyear + '.xlsx';


#Generating and exporting PO Records	
PORecords.to_excel("PORecords_output.xlsx")

#Generating and exporting Invoice
#rearranging columns of result dataframe and sorting by PO SR NO and excluded MTOC column
result = result.loc[:,['CN NO','CN DATE','FROM','TO','PO NO','PO SR NO','VEHICLE TYPE','WEIGHT MT','Extra Collection Additions','AMOUNT']].sort_values(by = ['PO NO','PO SR NO'])
result.to_excel(INVOICE_FILE_NAME)

#Generating PO Status
PORecords['Total Alloted'] = PORecords['PO_K160164_QTY'] + PORecords['PO_XXXXX_QTY'].fillna(0)
PORecords['Open PO Qty'] = PORecords['PO_K160164_REMAINING'] + PORecords['PO_XXXXX_REMAINING'].fillna(0)
PORecords['PERCENTAGE LEFT'] =  PORecords['Open PO Qty']/PORecords['Total Alloted']
PORecords = PORecords[PORecords['PERCENTAGE LEFT'] <= 0.500000]

PORecords.sort_values('PERCENTAGE LEFT')[['UOM SHORT','Open PO Qty','Total Alloted']].plot(x='UOM SHORT', kind = 'barh' ,ylabel = 'Quantity',title = 'UOM <= 50% of alloted PO remaining', rot = 0, color = ['#FF5252','#26A69A'])
plt.grid(axis= 'x', which='both', color='#082032', linewidth=0.25)
plt.minorticks_on()
plt.show()


