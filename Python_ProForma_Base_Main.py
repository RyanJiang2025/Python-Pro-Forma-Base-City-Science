from math import nan
import pandas as pd
import numpy as np
import numpy_financial as nf

from Python_ProForma_Inputs import Input_factors, Building_Specifications as BuildSpecs, Construction_Costs, Building_Type_rent_upkeep as RentUpkeep, Miscellaneous_Items as MiscItems, Building_Type
from Python_ProForma_Reforms import Reform_effects as Reforms

MiscItems["Years of Delay"] += Reforms["Delays Changes"]


ProForma_Table = pd.DataFrame(
    index=["Rent", "Hard Costs", "Soft Costs", "Land Costs", "Upkeep", "Net Operating Income", "Other Expenses", "Debt Inflow/Outflow", "Remaining Debt", "Property Sold Inflow", "Pre-Tax Cash Flow"],
    columns=range(MiscItems["Periods"]+2)
)

def Property_Sell_value(final_period):
    return ProForma_Table.at["Net Operating Income", final_period + 1] * MiscItems["Exit Value Multiple"]

def Core_and_Corridoor_Upkeep(): #Core and corridoor costs are already included in construction costs
    return (RentUpkeep.at["Elevator", "upkeep"] * BuildSpecs["Elevator_per_floor"] * (1 + Reforms["Elevator Upkeep"]) + RentUpkeep.at["Stairwell", "upkeep"] * BuildSpecs["Stairwell_per_floor"] * (1 + Reforms["Stairwell Upkeep"]) + RentUpkeep.at[Building_Type, "upkeep"] * BuildSpecs["Corridoor_size_per_floor"] * (1 + Reforms["Corridoor Upkeep"])) * 12 * BuildSpecs["Stories"]
#NOTE Need to still add this into the pro forma table without breaking everything.

def Rent_Upkeep_Multiplier(Rent_or_Upkeep, Type, Area, Vacancy, Months, reform_effect):
    return (RentUpkeep.at[Type, Rent_or_Upkeep] * BuildSpecs[Area]) * Months * (1 - Vacancy) * (1 + reform_effect)


#==========================================

def Period_0_ProForma(Table):
    Relevant_table = Table
    Relevant_table.at["Rent", 0] = 0
    Relevant_table.at["Hard Costs", 0] = Construction_Costs["Total_ex_land"] * (1 + Reforms["Hard Costs"])
    Relevant_table.at["Soft Costs", 0] = Relevant_table.at["Hard Costs", 0] * MiscItems["Soft costs"] * (1 + Reforms["Soft Costs"])
    Relevant_table.at["Land Costs", 0] = Construction_Costs["Land"] * (1 + Reforms["Land Costs"])
    Relevant_table.at["Upkeep", 0] = 0
    Relevant_table.at["Net Operating Income", 0] = 0
    Relevant_table.at["Other Expenses", 0] = 0
    Relevant_table.at["Debt Inflow/Outflow", 0] = abs(Relevant_table.at["Hard Costs", 0] * MiscItems["Debt"])
    Relevant_table.at["Remaining Debt", 0] = Relevant_table.at["Hard Costs", 0] * MiscItems["Debt"]
    Relevant_table.at["Property Sold Inflow", 0] = 0
    Relevant_table.at["Pre-Tax Cash Flow", 0] = Relevant_table.at["Hard Costs", 0] + Relevant_table.at["Soft Costs", 0] + Relevant_table.at["Land Costs", 0] + Relevant_table.at["Debt Inflow/Outflow", 0]

def Period_1_ProForma(): #no delay
    ProForma_Table.at["Rent", 1] = Rent_Upkeep_Multiplier("rent", Building_Type, "Rentable_area_residential", MiscItems["Vacancy Rate"], 12, Reforms["Rent Residential"]) + Rent_Upkeep_Multiplier("rent", "Retail_floors", "Rentable_area_retail", MiscItems["Vacancy Rate"], 12, Reforms["Rent Retail"])
    ProForma_Table.at["Upkeep", 1] = Rent_Upkeep_Multiplier("upkeep", Building_Type, "Rentable_area_residential", MiscItems["Vacancy Rate"], 12, Reforms["Upkeep Residential"]) + Rent_Upkeep_Multiplier("upkeep", "Retail_floors", "Rentable_area_retail", MiscItems["Vacancy Rate"], 12, Reforms["Upkeep Retail"]) + Core_and_Corridoor_Upkeep()
    ProForma_Table.at["Net Operating Income", 1] = ProForma_Table.at["Rent", 1] + ProForma_Table.at["Upkeep", 1]
    ProForma_Table.at["Other Expenses", 1] = ProForma_Table.at["Net Operating Income", 1] * MiscItems["Other Expenses"]
    ProForma_Table.at["Debt Inflow/Outflow", 1] = -ProForma_Table.at["Debt Inflow/Outflow", 0] * MiscItems["Mortgage Constant No Delay"]
    ProForma_Table.at["Remaining Debt", 1] = (ProForma_Table.at["Remaining Debt", 0] * (1 + MiscItems["Debt Interest Rate"])) - ProForma_Table.at["Debt Inflow/Outflow", 1]   
    ProForma_Table.at["Property Sold Inflow", 1] = 0
    ProForma_Table.at["Pre-Tax Cash Flow", 1] = ProForma_Table.at["Net Operating Income", 1] + ProForma_Table.at["Other Expenses", 1] + ProForma_Table.at["Debt Inflow/Outflow", 1]
    
    ProForma_Table.at["Hard Costs", 1] = 0
    ProForma_Table.at["Soft Costs", 1] = 0
    ProForma_Table.at["Land Costs", 1] = 0

def Period_2plus_ProForma(period): #no delay
    ProForma_Table.at["Rent", period] = ProForma_Table.at["Rent", period-1] * (1 + MiscItems["Rent Increase Rate"])
    ProForma_Table.at["Upkeep", period] = ProForma_Table.at["Upkeep", period-1] * (1 + MiscItems["Upkeep Increase Rate"]) + Core_and_Corridoor_Upkeep()
    ProForma_Table.at["Net Operating Income", period] = ProForma_Table.at["Rent", period] + ProForma_Table.at["Upkeep", period]
    ProForma_Table.at["Other Expenses", period] = ProForma_Table.at["Net Operating Income", period] * MiscItems["Other Expenses"]
    ProForma_Table.at["Debt Inflow/Outflow", period] = -ProForma_Table.at["Debt Inflow/Outflow", 0] * MiscItems["Mortgage Constant No Delay"] if period <= MiscItems["Periods"] else 0
    ProForma_Table.at["Remaining Debt", period] = (ProForma_Table.at["Remaining Debt", period-1] * (1 + MiscItems["Debt Interest Rate"])) - ProForma_Table.at["Debt Inflow/Outflow", period]
    ProForma_Table.at["Property Sold Inflow", period] = 0
    ProForma_Table.at["Pre-Tax Cash Flow", period] = ProForma_Table.at["Net Operating Income", period] + ProForma_Table.at["Other Expenses", period] + ProForma_Table.at["Debt Inflow/Outflow", period]

    ProForma_Table.at["Hard Costs", period] = 0
    ProForma_Table.at["Soft Costs", period] = 0
    ProForma_Table.at["Land Costs", period] = 0

for period in range(MiscItems["Periods"] + 2): #+2 because of zero indexing
    if period == 0:
        Period_0_ProForma(ProForma_Table)
    elif period == 1:
        Period_1_ProForma()
    else:
        Period_2plus_ProForma(period)

ProForma_Table.at["Property Sold Inflow", MiscItems["Periods"]] = Property_Sell_value(MiscItems["Periods"])
ProForma_Table.at["Pre-Tax Cash Flow", MiscItems["Periods"]] += ProForma_Table.at["Property Sold Inflow", MiscItems["Periods"]]

ProForma_Table_Delay = pd.DataFrame(
    index=["Rent", "Hard Costs", "Soft Costs", "Land Costs", "Upkeep", "Net Operating Income", "Other Expenses", "Debt Inflow/Outflow", "Remaining Debt", "Property Sold Inflow", "Pre-Tax Cash Flow"],
    columns=range(MiscItems["Periods"]+2)
)

def Period_1_ProForma_Delay(): #no delay
    ProForma_Table_Delay.at["Rent", 1] = ProForma_Table.at["Rent", 1] if period > MiscItems["Years of Delay"] else 0   
    ProForma_Table_Delay.at["Upkeep", 1] = ProForma_Table.at["Upkeep", 1] if period > MiscItems["Years of Delay"] else 0
    ProForma_Table_Delay.at["Net Operating Income", 1] = ProForma_Table_Delay.at["Rent", 1] + ProForma_Table_Delay.at["Upkeep", 1]
    ProForma_Table_Delay.at["Other Expenses", 1] = ProForma_Table.at["Other Expenses", 1]
    ProForma_Table_Delay.at["Debt Inflow/Outflow", 1] = -ProForma_Table_Delay.at["Debt Inflow/Outflow", 0] * MiscItems["Mortgage Constant With Delay"] if period > MiscItems["Years of Delay"] else 0
    ProForma_Table_Delay.at["Remaining Debt", 1] = (ProForma_Table_Delay.at["Remaining Debt", 0] * (1 + MiscItems["Debt Interest Rate"])) - ProForma_Table_Delay.at["Debt Inflow/Outflow", 1]   
    ProForma_Table_Delay.at["Property Sold Inflow", 1] = 0
    ProForma_Table_Delay.at["Pre-Tax Cash Flow", 1] = ProForma_Table_Delay.at["Net Operating Income", 1] + ProForma_Table_Delay.at["Other Expenses", 1] + ProForma_Table_Delay.at["Debt Inflow/Outflow", 1]
    
    ProForma_Table_Delay.at["Hard Costs", 1] = 0
    ProForma_Table_Delay.at["Soft Costs", 1] = 0
    ProForma_Table_Delay.at["Land Costs", 1] = 0

def Period_2plus_ProForma_Delay(period): #no delay
    ProForma_Table_Delay.at["Rent", period] = ProForma_Table.at["Rent", period] if period > MiscItems["Years of Delay"] else 0
    ProForma_Table_Delay.at["Upkeep", period] = ProForma_Table.at["Upkeep", period] if period > MiscItems["Years of Delay"] else 0
    ProForma_Table_Delay.at["Net Operating Income", period] = ProForma_Table_Delay.at["Rent", period] + ProForma_Table_Delay.at["Upkeep", period]
    ProForma_Table_Delay.at["Other Expenses", period] = ProForma_Table_Delay.at["Net Operating Income", period] * MiscItems["Other Expenses"]
    ProForma_Table_Delay.at["Debt Inflow/Outflow", period] = -ProForma_Table_Delay.at["Debt Inflow/Outflow", 0] * MiscItems["Mortgage Constant With Delay"] if period <= MiscItems["Periods"] else 0
    ProForma_Table_Delay.at["Remaining Debt", period] = (ProForma_Table_Delay.at["Remaining Debt", period-1] * (1 + MiscItems["Debt Interest Rate"])) - ProForma_Table_Delay.at["Debt Inflow/Outflow", period]
    ProForma_Table_Delay.at["Property Sold Inflow", period] = 0
    ProForma_Table_Delay.at["Pre-Tax Cash Flow", period] = ProForma_Table_Delay.at["Net Operating Income", period] + ProForma_Table_Delay.at["Other Expenses", period] + ProForma_Table_Delay.at["Debt Inflow/Outflow", period]

    ProForma_Table_Delay.at["Hard Costs", period] = 0
    ProForma_Table_Delay.at["Soft Costs", period] = 0
    ProForma_Table_Delay.at["Land Costs", period] = 0

for period in range(MiscItems["Periods"] + 2): #+2 because of zero indexing
    if period == 0:
        Period_0_ProForma(ProForma_Table_Delay)
    elif period == 1:
        Period_1_ProForma_Delay()
    else:
        Period_2plus_ProForma_Delay(period)

ProForma_Table_Delay.at["Property Sold Inflow", MiscItems["Periods"]] = Property_Sell_value(MiscItems["Periods"])
ProForma_Table_Delay.at["Pre-Tax Cash Flow", MiscItems["Periods"]] += ProForma_Table_Delay.at["Property Sold Inflow", MiscItems["Periods"]]

#==========================================

print("==================== ProForma Calculator ====================")
print("--------------------------------")
print("Input Factors")
print(Input_factors)
print("--------------------------------")
print("Building Specifications")
print(BuildSpecs)
print("--------------------------------")
print("Construction Costs")
print(Construction_Costs)
print("--------------------------------")
print("Rent and Upkeep")
print(RentUpkeep)
print("--------------------------------")
print("Core and Corridoor Upkeep")
print(Core_and_Corridoor_Upkeep())
print("--------------------------------")
print("Miscellaneous Items")
print(MiscItems)
print("--------------------------------")

#==========================================
#Note that because some items are calculated assuming no delay even in the delay table (for example other expenses as a percentage of NOI), the delay table only functions when we calculate the no delay table first.
print("ProForma Table :", MiscItems["Periods"], "periods")
print(ProForma_Table.loc[:, :MiscItems["Periods"]])

print()
print("IRR: ", round(nf.irr(ProForma_Table.loc["Pre-Tax Cash Flow", :MiscItems["Periods"]].values) * 100, 2), "%")
print("NPV: ", "$" + str(round(nf.npv(MiscItems["Discount Rate"], ProForma_Table.loc["Pre-Tax Cash Flow", :MiscItems["Periods"]].values), 2)))

print("--------------------------------")

if MiscItems["Years of Delay"] > 0:
    print("ProForma Table with Delay :", MiscItems["Years of Delay"], "years of delay,", MiscItems["Periods"], "periods")
    print(ProForma_Table_Delay.loc[:, :MiscItems["Periods"]])

print()
print("IRR: ", round(nf.irr(ProForma_Table_Delay.loc["Pre-Tax Cash Flow", :MiscItems["Periods"]].values) * 100, 2), "%")
print("NPV: ", "$" + str(round(nf.npv(MiscItems["Discount Rate"], ProForma_Table_Delay.loc["Pre-Tax Cash Flow", :MiscItems["Periods"]].values), 2)))
print("--------------------------------")