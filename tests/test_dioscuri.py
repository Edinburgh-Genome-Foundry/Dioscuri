import dioscuri


def test_dioscuri():
    aspirate = dioscuri.Pipette(
        "Aspirate", "Source1", "4ti-0960/B on raised carrier", "3", "50"
    )
    aspirate.to_string()

    dispense = dioscuri.Pipette("D", "Destination", "4ti-0960/B on CPAC", "1", "50")

    wash = dioscuri.WashTipOrReplaceDITI(scheme=2)

    worklist = dioscuri.GeminiWorkList(
        name="my_worklist", records=[aspirate, dispense, wash]
    )
    gwl_string = worklist.records_to_string()

    assert (
        gwl_string == "A;Source1;;4ti-0960/B on raised carrier;3;;50;;;;\n"
        "D;Destination;;4ti-0960/B on CPAC;1;;50;;;;\nW2;\n"
    )
