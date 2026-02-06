from math import nan
import Python_ProForma_Inputs as pfi
import pandas as pd
import numpy as np
import numpy_financial as nf

Delay_Boolean = True

for item in 

ProForma_Table = pd.DataFrame(
    index=["Rent", "Hard Costs", "Soft Costs", "Land Costs", "Upkeep", "Net Operating Income", "Other Expenses", "Debt Inflow/Outflow", "Remaining Debt", "Property Sold Inflow", "Pre-Tax Cash Flow"],
    columns=range(pfi.Miscellaneous_Items["Periods"]+2)
)
#NOTE Delay stuff needs to be recalculated; right now delay only affects debt and not rent or upkeep.


def Period_0_ProForma(Delay_Boolean):
    ProForma_Table.loc["Rent", 0] = 0
    ProForma_Table.loc["Hard Costs", 0] = pfi.Construction_Costs["Total_ex_land"]
    ProForma_Table.loc["Soft Costs", 0] = pfi.Construction_Costs["Total_ex_land"] * pfi.Miscellaneous_Items["Soft costs"]
    ProForma_Table.loc["Land Costs", 0] = pfi.Construction_Costs["Land"]
    ProForma_Table.loc["Upkeep", 0] = 0
    ProForma_Table.loc["Net Operating Income", 0] = 0
    ProForma_Table.loc["Other Expenses", 0] = 0
    ProForma_Table.loc["Debt Inflow/Outflow", 0] = ProForma_Table.loc["Hard Costs", 0] * pfi.Miscellaneous_Items["Debt"]
    ProForma_Table.loc["Remaining Debt", 0] = ProForma_Table.loc["Debt Inflow/Outflow", 0]
    ProForma_Table.loc["Property Sold Inflow", 0] = 0
    ProForma_Table.loc["Pre-Tax Cash Flow", 0] = ProForma_Table.loc["Hard Costs", 0] + ProForma_Table.loc["Soft Costs", 0] + ProForma_Table.loc["Land Costs", 0] + ProForma_Table.loc["Debt Inflow/Outflow", 0]

def Period_1_ProForma(Delay_Boolean):
    ProForma_Table.loc["Hard Costs", 1] = 0
    ProForma_Table.loc["Soft Costs", 1] = 0
    ProForma_Table.loc["Land Costs", 1] = 0
    if Delay_Boolean == True and pfi.Miscellaneous_Items["Years of Delay"] >= 1:
        ProForma_Table.loc["Rent", 1] = 0
        ProForma_Table.loc["Upkeep", 1] = 0
    else:
        ProForma_Table.loc["Rent", 1] = (pfi.Building_Specifications["Rentable_area_residential"] * pfi.Building_Type_rent_upkeep.loc[pfi.Building_Type, "rent"] + pfi.Building_Specifications["Rentable_area_retail"] * pfi.Building_Type_rent_upkeep.loc["Retail_floors", "rent"]) * (1 - pfi.Miscellaneous_Items["Vacancy Rate"])
        ProForma_Table.loc["Upkeep", 1] = (pfi.Building_Specifications["Rentable_area_residential"] * pfi.Building_Type_rent_upkeep.loc[pfi.Building_Type, "upkeep"] + pfi.Building_Specifications["Rentable_area_retail"] * pfi.Building_Type_rent_upkeep.loc["Retail_floors", "upkeep"]) * (1 - pfi.Miscellaneous_Items["Vacancy Rate"])
    ProForma_Table.loc["Net Operating Income", 1] = ProForma_Table.loc["Rent", 1] + ProForma_Table.loc["Upkeep", 1]
    ProForma_Table.loc["Other Expenses", 1] = ProForma_Table.loc["Net Operating Income", 1] * pfi.Miscellaneous_Items["Other Expenses"]
    ProForma_Table.loc["Debt Inflow/Outflow", 1] = ProForma_Table.loc["Remaining Debt", 0] * pfi.Miscellaneous_Items["Mortgage Constant No Delay"] if Delay_Boolean == False else 0
    ProForma_Table.loc["Remaining Debt", 1] = ProForma_Table.loc["Remaining Debt", 0] * (1 + pfi.Miscellaneous_Items["Debt Interest Rate"]) - ProForma_Table.loc["Debt Inflow/Outflow", 1]
    ProForma_Table.loc["Property Sold Inflow", 1] = 0
    ProForma_Table.loc["Pre-Tax Cash Flow", 1] = ProForma_Table.loc["Net Operating Income", 1] + ProForma_Table.loc["Other Expenses", 1] + ProForma_Table.loc["Debt Inflow/Outflow", 1]

def Period_2_plus_ProForma(Delay_Boolean):
    for period in range(2, pfi.Miscellaneous_Items["Periods"]+2):
        if Delay_Boolean == False: #no delay
            ProForma_Table.loc["Rent", period] = (ProForma_Table.loc["Rent", period - 1] * (1 + pfi.Miscellaneous_Items["Rent Increase Rate"]))
            ProForma_Table.loc["Upkeep", period] = (ProForma_Table.loc["Upkeep", period - 1] * (1 + pfi.Miscellaneous_Items["Upkeep Increase Rate"]))
        elif Delay_Boolean == True and pfi.Miscellaneous_Items["Years of Delay"] >= period: #delay period
            ProForma_Table.loc["Rent", period] = 0
            ProForma_Table.loc["Upkeep", period] = 0
        else: #delay present but not in period
            ProForma_Table.loc["Rent", period] = No_Delay_ProForma_Table.loc["Rent", period]
            ProForma_Table.loc["Upkeep", period] = No_Delay_ProForma_Table.loc["Upkeep", period]
        ProForma_Table.loc["Hard Costs", period] = 0
        ProForma_Table.loc["Soft Costs", period] = 0
        ProForma_Table.loc["Land Costs", period] = 0
        ProForma_Table.loc["Net Operating Income", period] = ProForma_Table.loc["Rent", period] + ProForma_Table.loc["Upkeep", period]
        ProForma_Table.loc["Other Expenses", period] = No_Delay_ProForma_Table.loc["Other Expenses", period]
        if Delay_Boolean == False:
            ProForma_Table.loc["Debt Inflow/Outflow", period] = ProForma_Table.loc["Debt Inflow/Outflow", 0] * pfi.Miscellaneous_Items["Mortgage Constant No Delay"]
        elif Delay_Boolean == True and pfi.Miscellaneous_Items["Years of Delay"] >= period:
            ProForma_Table.loc["Debt Inflow/Outflow", period] = 0
            ProForma_Table.loc["Rent", period] = 0
            ProForma_Table.loc["Upkeep", period] = 0
        else:
            ProForma_Table.loc["Debt Inflow/Outflow", period] = ProForma_Table.loc["Remaining Debt", pfi.Miscellaneous_Items["Years of Delay"]] * pfi.Miscellaneous_Items["Mortgage Constant With Delay"]
            if period == pfi.Miscellaneous_Items["Years of Delay"]+1:
                ProForma_Table.loc["Rent", period] = (pfi.Building_Specifications["Rentable_area_residential"] * pfi.Building_Type_rent_upkeep.loc[pfi.Building_Type, "rent"] + pfi.Building_Specifications["Rentable_area_retail"] * pfi.Building_Type_rent_upkeep.loc["Retail_floors", "rent"]) * (1 - pfi.Miscellaneous_Items["Vacancy Rate"]) * (1+pfi.Miscellaneous_Items["Rent Increase Rate"])**(period)
                ProForma_Table.loc["Upkeep", period] = (pfi.Building_Specifications["Rentable_area_residential"] * pfi.Building_Type_rent_upkeep.loc[pfi.Building_Type, "upkeep"] + pfi.Building_Specifications["Rentable_area_retail"] * pfi.Building_Type_rent_upkeep.loc["Retail_floors", "upkeep"]) * (1 - pfi.Miscellaneous_Items["Vacancy Rate"]) * (1+pfi.Miscellaneous_Items["Upkeep Increase Rate"])**(period)
        ProForma_Table.loc["Remaining Debt", period] = ProForma_Table.loc["Remaining Debt", period-1] * (1 + pfi.Miscellaneous_Items["Debt Interest Rate"]) - ProForma_Table.loc["Debt Inflow/Outflow", period]
        ProForma_Table.loc["Property Sold Inflow", period] = 0 #Change to actual property sold inflow
        ProForma_Table.loc["Pre-Tax Cash Flow", period] = ProForma_Table.loc["Net Operating Income", period] + ProForma_Table.loc["Other Expenses", period] + ProForma_Table.loc["Debt Inflow/Outflow", period] + ProForma_Table.loc["Property Sold Inflow", period]


#This code down here may not be needed; but since we need end period + 1's NOI to calculate the property sold inflow, we need to replace it in period 1 if we only have 1 period.
if pfi.Miscellaneous_Items["Periods"] == 1:
    ProForma_Table.loc["Property Sold Inflow", 1] = ProForma_Table.loc["Net Operating Income", 2] * pfi.Miscellaneous_Items["Exit Value Multiple"]
    ProForma_Table.loc["Pre-Tax Cash Flow", 1] = ProForma_Table.loc["Pre-Tax Cash Flow", 1] + ProForma_Table.loc["Property Sold Inflow", 1]

def No_Delay_ProForma():
    Period_0_ProForma(False)
    Period_1_ProForma(False)
    

No_Delay_ProForma_Table = No_Delay_ProForma()

def Delay_ProForma():
    Period_0_ProForma(True)
    Period_1_ProForma(True)

Delay_ProForma_Table = Delay_ProForma()

#==========================================
print("ProForma Table")
print(ProForma_Table)