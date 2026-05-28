# Workbook Indexing Review

Workbook: `/Users/mancunian_naz/Downloads/DDDM-Dev/Final Data Tables for Subscription Model-V15.xlsx`

| Sheet | Rows | Columns | Recommendation | Reason |
| --- | ---: | ---: | --- | --- |
| Semantic Model | 36 | 7 | include | Known metadata/routing workbook sheet. |
| Final-Columns with Lookup | 174 | 77 | include | Known metadata/routing workbook sheet. |
| Table Names | 28 | 6 | include | Known metadata/routing workbook sheet. |
| Tables & Attributes | 38 | 23 | include | Known metadata/routing workbook sheet. |
| Final Data Tables | 33 | 10 | include | Known metadata/routing workbook sheet. |
| Questions | 32 | 8 | include | Known metadata/routing workbook sheet. |
| Measures Semantic Model | 58 | 5 | include | Known metadata/routing workbook sheet. |
| General Mapping | 5 | 7 | include | Known metadata/routing workbook sheet. |

## Semantic Model

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

Sl.No, Semantic Model, Tables, Filter based
on the 
column A, Status, Date, Internal Testing

Sample rows:

```json
[
  {
    "Sl.No": "1",
    "Semantic Model": "dddm_sm_subscription",
    "Tables": "MemberTrans",
    "Filter based\non the \ncolumn A": "1-14",
    "Status": "Completed",
    "Date": "2026-05-09 00:00:00"
  },
  {
    "Tables": "MemberTransTypes"
  },
  {
    "Tables": "Member"
  }
]
```

## Final-Columns with Lookup

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

#, Sl.
No, DataFlow Gen2 Name, Status, Samentic Model, Source Table Name, Type, Table Type, Data Type, Source-Column, Key, #, Lookup-Column, Lookup-Table, Comments, Comments-2

Sample rows:

```json
[
  {
    "#": "1",
    "Sl.\nNo": "1",
    "DataFlow Gen2 Name": "dddm_df_subscription",
    "Status": "Uploaded",
    "Samentic Model": "dddm_sm_subscription",
    "Source Table Name": "MemberTrans",
    "Type": "Subscription",
    "Table Type": "Physical",
    "Data Type": "TD",
    "Source-Column": "Id",
    "Key": "PK"
  },
  {
    "#": "1",
    "Source-Column": "Transtype",
    "Key": "FK",
    "Lookup-Column": "TransTypeId",
    "Lookup-Table": "MemberTransTypes"
  },
  {
    "#": "1",
    "Source-Column": "degree",
    "Key": "FK",
    "Lookup-Column": "Id",
    "Lookup-Table": "Degree"
  }
]
```

## Table Names

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

Abb, #, Table
Type, Table Name

Sample rows:

```json
[
  {
    "Abb": "met",
    "#": "1",
    "Table\nType": "TD",
    "Table Name": "MemberTrans"
  },
  {
    "Abb": "mtt",
    "#": "2",
    "Table\nType": "MD",
    "Table Name": "MemberTransTypes"
  },
  {
    "Abb": "mem",
    "#": "3",
    "Table\nType": "MD",
    "Table Name": "Member"
  }
]
```

## Tables & Attributes

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

Sl.No, Source Table Name, Table Type, Data Type, Column1, Column2, Column3, Column4, Column5, Column6, Column7, Column8, Column9, Column10, Column11, Column12, Column13, Column14, Column15, Column16, Column17, Column18, Comments

Sample rows:

```json
[
  {
    "Sl.No": "1",
    "Source Table Name": "dwe.MemberTrans",
    "Table Type": "Physical",
    "Data Type": "TD",
    "Column1": "Id",
    "Column2": "Transtype",
    "Column3": "degree",
    "Column4": "NextYearDegree",
    "Column5": "MemberID",
    "Column6": "RenewDate",
    "Column7": "expiryDate"
  },
  {
    "Sl.No": "2",
    "Source Table Name": "dwe.TranType",
    "Table Type": "Zameer"
  },
  {
    "Sl.No": "3",
    "Source Table Name": "dwe.Member",
    "Table Type": "Physical",
    "Data Type": "MD",
    "Column1": "Id",
    "Column2": "Regtype",
    "Column3": "Directionsflssueld",
    "Column4": "ClassCommRegId",
    "Column5": "DegreeId",
    "Column6": "RegDate",
    "Column7": "RenewDate",
    "Column8": "ExpiryDate",
    "Column9": "NationalityId",
    "Column10": "OwnerType",
    "Column11": "CaptialPaid",
    "Column12": "SALabor",
    "Column13": "Flag",
    "Column14": "MemberSource",
    "Column15": "ThiqahActivites",
    "Column16": "FSC_CityID"
  }
]
```

## Final Data Tables

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

Source Table Name, Orginal Table Name, To-Be View Name, Table Type, Present Table Type, TO-BE Table Type, Present Schema Name, TO-BE Schema Name, Relation, Comments

Sample rows:

```json
[
  {
    "Source Table Name": "vw_Starways_MemberTrans (Cube)",
    "Orginal Table Name": "MemberTrans",
    "To-Be View Name": "MemberTrans",
    "Table Type": "Physical",
    "Present Table Type": "Physical",
    "TO-BE Table Type": "View",
    "Present Schema Name": "dbo",
    "Relation": "Fact Data"
  },
  {
    "Source Table Name": "TranType",
    "Orginal Table Name": "TranType",
    "To-Be View Name": "TranType",
    "Table Type": "Physical",
    "Present Table Type": "Physical",
    "TO-BE Table Type": "View",
    "Present Schema Name": "dbo",
    "Relation": "Dim Data",
    "Comments": "This view will be created based on the logic provided by Naser (as agreed Naseer will create a view and provided the access) (Naser will create this view from his side)"
  },
  {
    "Source Table Name": "vw_Starways_Member",
    "Orginal Table Name": "Member",
    "To-Be View Name": "Member",
    "Table Type": "Physical",
    "Present Table Type": "Physical",
    "TO-BE Table Type": "View",
    "Present Schema Name": "dbo",
    "Relation": "Dim Data"
  }
]
```

## Questions

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

Sl.No, AI Query, Samentic Layer, Table Names, SQL Statement, Notes, Metadata

Sample rows:

```json
[
  {
    "AI Query": "A.\tأسئلة عددية مباشرة:",
    "Notes": "use TransDate for every Date\nTransDate: تاريخ تحصيل/الحركة\nRenewDate: تاريخ التجديد\nexpiryDate(اخر status): تاريخ الانتهاء"
  },
  {
    "Sl.No": "1",
    "Column 2": "كم عدد الإشتراكات الجديدة هذا الشهر؟ (بلغ عدد العضويات الجديدة خلال شهر [X] عدد [1234] عضوية.)",
    "AI Query": "How many new subscriptions are there this month? (The number of new memberships during month [X] was [1,234] memberships.)",
    "Samentic Layer": "dddm_sm_subscription",
    "Table Names": "MemberTrans\nMemberTransTypes\nVoucherHeader",
    "SQL Statement": "SELECT count(1) as new_cnt_sub\nfrom memebertrans as mt\ninner join voucherheader as vh\non mt.id = vh.MemberTransId\ninner join membertranstypes as mtt\non mtt.TransTypeId = mt.transtype\nwhere mt.transtype = 1 and vh.TransDate = month(getdate())",
    "Metadata": "الاشتراكات الجديدة  = العضويات الجديدة = كم عدد الجدد"
  },
  {
    "Sl.No": "2",
    "Column 2": "كم عدد العضويات المجدده هذا الربع ؟ (بلغ عدد العضويات المجددة خلال الربع [QX] عدد [XXX].)",
    "AI Query": "How many memberships were renewed this quarter? (The number of renewed memberships during [QX] quarter was [XXX].)",
    "Samentic Layer": "dddm_sm_subscription",
    "Table Names": "MemberTrans\nMemberTransTypes\nVoucherHeader",
    "SQL Statement": "SELECT count(1) as new_cnt_sub\nfrom memebertrans as mt\ninner join voucherheader as vh\non mt.id = vh.MemberTransId\ninner join membertranstypes as mtt\non mtt.TransTypeId = mt.transtype\nwhere mt.transtype = 2 and vh.TransDate = datepart(quarter, getdate()) as CurrentQuarter \nAnd vh.TransDate = datepart"
  }
]
```

## Measures Semantic Model

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

#, Semantic Model, Date Column, Measure Name, DAX Formula

Sample rows:

```json
[
  {
    "#": "1",
    "Semantic Model": "dddm_sm_subscription",
    "Date Column": "VoucherHeader[TransDate]",
    "Measure Name": "Active Members",
    "DAX Formula": "CALCULATE(COUNTROWS(Member), Member[ExpiryDate] >= TODAY())"
  },
  {
    "#": "2",
    "Semantic Model": "dddm_sm_subscription",
    "Date Column": "VoucherHeader[TransDate]",
    "Measure Name": "Activity Records",
    "DAX Formula": "COUNTROWS(MemberActivityICEC4)"
  },
  {
    "#": "3",
    "Semantic Model": "dddm_sm_subscription",
    "Date Column": "VoucherHeader[TransDate]",
    "Measure Name": "Average Subscription Payment",
    "DAX Formula": "DIVIDE([Total Subscription Payment], [Subscription Voucher Count])"
  }
]
```

## General Mapping

Recommendation: **include**

Reason: Known metadata/routing workbook sheet.

Headers:

Arabic User Term, English Term, Semantic Model, Measure Name, Default Date Column, Allowed Dimensions, Requires Clarification

Sample rows:

```json
[
  {
    "Arabic User Term": "الاشتراكات الجديدة",
    "English Term": "New subscriptions",
    "Semantic Model": "dddm_sm_subscription",
    "Measure Name": "New Subscription",
    "Default Date Column": "VoucherHeader[TransDate]",
    "Allowed Dimensions": "Branch, City, Degree, Activity, Month, Quarter, Year",
    "Requires Clarification": "No"
  },
  {
    "Arabic User Term": "العضويات المجددة",
    "English Term": "Renewed memberships",
    "Semantic Model": "dddm_sm_subscription",
    "Measure Name": "Renewed Memberships",
    "Default Date Column": "VoucherHeader[TransDate]",
    "Allowed Dimensions": "Branch, City, Degree, Month, Quarter, Year",
    "Requires Clarification": "No"
  },
  {
    "Arabic User Term": "التصاديق اليدوية",
    "English Term": "Manual attestations",
    "Semantic Model": "dddm_sm_manualstamp",
    "Measure Name": "Manual Attestations",
    "Default Date Column": "SignCollHeader[TransDate]",
    "Allowed Dimensions": "Branch, Treatment Type, Month, Quarter, Year",
    "Requires Clarification": "Maybe branch/date"
  }
]
```
