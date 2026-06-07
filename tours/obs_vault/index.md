---
type: index
---
# StepByStep — Vault Index

## Tours

| Tour | Beschrijving |
|------|-------------|
| [[tours/parisii_tot_napoleon/00-wandelroute\|Van Parisii tot Napoleon]] | 2000 jaar Parijse machtgeschiedenis, 13 stops |

```dataview
TABLE nummer as "#", periode as "Periode"
FROM "tours/parisii_tot_napoleon/stops"
SORT nummer ASC
```

## Personen
```dataview
LIST FROM "personen" SORT file.name ASC
```

## Periodes
```dataview
LIST FROM "periodes" SORT file.name ASC
```

## Concepten
```dataview
LIST FROM "concepten" SORT file.name ASC
```

## Plaatsen
```dataview
LIST FROM "plaatsen" SORT file.name ASC
```

## Zie ook
- [[lutetia]]
- [[ile-de-la-cite]]
- [[linkeroever-rive-gauche]]
