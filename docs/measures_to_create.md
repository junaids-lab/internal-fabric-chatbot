# Semantic Model Measures To Confirm

The backend DAX templates assume these measures already exist in the four semantic models.

Important: the examples in this first section are model measure definitions. Add them from the semantic model measure editor, Power BI Desktop modeling view, Tabular Editor, or Fabric semantic model authoring.

If you paste `New Subscription = ...` directly into a DAX query window or the Power BI Execute Queries API, you will get a syntax error such as `The syntax for 'New' is incorrect`. DAX queries must use `DEFINE MEASURE ... EVALUATE ...`; see the testing section below.

## dddm_sm_subscription

```DAX
New Subscription =
CALCULATE(
    COUNTROWS('MemberTrans'),
    'MemberTrans'[Transtype] = 1
)

Renewed Memberships =
CALCULATE(
    COUNTROWS('MemberTrans'),
    'MemberTrans'[Transtype] = 2
)

Cancelled Subscriptions =
CALCULATE(
    COUNTROWS('MemberTrans'),
    'MemberTrans'[Transtype] = 3
)
```

## dddm_sm_manualstamp

Confirm whether the business KPI counts header rows or detail rows.

```DAX
Manual Attestations =
COUNTROWS('SignCollDetail')
```

## dddm_sm_electronicstamp

```DAX
Approved Electronic Attestations =
CALCULATE(
    COUNTROWS('ESFormContents'),
    'ESFormContents'[FormStatus] = 1
)
```

## dddm_sm_permit

```DAX
Total Permits =
[Competition Permits]
+ [Competition Extension Permits]
+ [Branch Permits]
+ [Promotional Permits]
+ [Reexport Certificate Permits]
```

Adjust measure names in `app/routing/templates.py` if your semantic models use different names.

## Testing Measures In A DAX Query

Use this form in DAX query view or through the Execute Queries API if the measure is not saved to the model yet:

```DAX
DEFINE
    MEASURE 'MemberTrans'[New Subscription] =
        CALCULATE(
            COUNTROWS('MemberTrans'),
            'MemberTrans'[Transtype] = 1
        )

EVALUATE
    ROW("value", [New Subscription])
```

With a date filter:

```DAX
DEFINE
    MEASURE 'MemberTrans'[New Subscription] =
        CALCULATE(
            COUNTROWS('MemberTrans'),
            'MemberTrans'[Transtype] = 1
        )

EVALUATE
    ROW(
        "value",
        CALCULATE(
            [New Subscription],
            'VoucherHeader'[TransDate] >= DATE(2026, 5, 1),
            'VoucherHeader'[TransDate] <= DATE(2026, 5, 24)
        )
    )
```

After the measure is saved to the semantic model, the query can be only:

```DAX
EVALUATE
    ROW("value", [New Subscription])
```
