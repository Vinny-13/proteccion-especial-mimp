let
    Source = PostgreSQL.Database(pServer, pDatabase),
    Admissions = Source{[Schema="mimp", Item="vw_admissions_flat"]}[Data]
in
    Admissions
