import pytest
import dioscuri


def test_dioscuri():
    # PIPETTE
    with pytest.raises(ValueError):
        dioscuri.Pipette(
            "Neither 'Aspirate' nor 'Dispense'",
            "Source1",
            "4ti-0960/B on raised carrier",
            "3",
            "50",
        )

    aspirate = dioscuri.Pipette(
        "Aspirate", "Source1", "4ti-0960/B on raised carrier", "3", "50"
    )
    aspirate.to_string()

    dispense = dioscuri.Pipette("D", "Destination", "4ti-0960/B on CPAC", "1", "50")

    # WASH
    assert dioscuri.WashTipOrReplaceDITI().to_string() == "W;"
    with pytest.raises(ValueError):
        dioscuri.WashTipOrReplaceDITI(scheme=5)  # should be between 1--4
    wash = dioscuri.WashTipOrReplaceDITI(scheme=2)

    # DECONTAMINATION
    assert dioscuri.Decontamination().to_string() == "WD;"

    # FLUSH
    assert dioscuri.Flush().to_string() == "F;"

    # BREAK
    assert dioscuri.Break().to_string() == "B;"

    # WORKLIST
    dioscuri.GeminiWorkList()  # defaults

    worklist = dioscuri.GeminiWorkList(
        name="my_worklist", records=[aspirate, dispense, wash]
    )

    with pytest.raises(AssertionError):
        worklist.add_record("Not a dioscuri record class")

    worklist.add_record(dioscuri.WashTipOrReplaceDITI())

    assert worklist.list_records() == ["A", "D", "W", "W"]

    gwl_string = worklist.records_to_string()

    assert (
        gwl_string == "A;Source1;;4ti-0960/B on raised carrier;3;;50;;;;\n"
        "D;Destination;;4ti-0960/B on CPAC;1;;50;;;;\nW2;\nW;\n"
    )
