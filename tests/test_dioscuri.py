import os
import pytest
import dioscuri


def test_dioscuri(tmpdir):
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

    # WORKLIST
    dioscuri.GeminiWorkList()  # defaults

    worklist = dioscuri.GeminiWorkList(
        name="my_worklist", records=[aspirate, dispense, wash]
    )

    with pytest.raises(AssertionError):
        worklist.add_record("Not a dioscuri record class")

    with pytest.raises(ValueError):
        worklist.add_record(dioscuri.SetDITIType("diti_index"))

    worklist.add_record(dioscuri.WashTipOrReplaceDITI())

    assert worklist.list_records() == ["A", "D", "W", "W"]

    # DECONTAMINATION
    decontaminate = dioscuri.Decontamination()
    assert decontaminate.to_string() == "WD;"
    worklist.add_record(decontaminate)

    # FLUSH
    flush = dioscuri.Flush()
    assert flush.to_string() == "F;"
    worklist.add_record(flush)

    # BREAK
    break_record = dioscuri.Break()
    assert break_record.to_string() == "B;"
    worklist.add_record(break_record)

    # SET DITI TYPE
    set_diti_type = dioscuri.SetDITIType("diti_index")
    assert set_diti_type.to_string() == "S;diti_index"
    worklist.add_record(set_diti_type)

    # COMMENT
    assert dioscuri.Comment("This is a comment").to_string() == "C;This is a comment"
    comment = dioscuri.Comment("Multiline\ncomment")
    assert comment.to_string() == "C;Multiline\\ncomment"
    worklist.add_record(comment)

    # REAGENT DISTRIBUTION
    reagent_dist = dioscuri.ReagentDistribution(
        "SrcRackLabel",
        "SrcRackID",
        "SrcRackType",
        "SrcPosStart",
        "SrcPosEnd",
        "DestRackLabel",
        "DestRackID",
        "DestRackType",
        "DestPosStart",
        "DestPosEnd",
        "Volume",
    )
    expected_string = (
        "R;SrcRackLabel;SrcRackID;SrcRackType;"
        "SrcPosStart;SrcPosEnd;DestRackLabel;DestRackID;DestRackType;DestPosStart;"
        "DestPosEnd;Volume;;1;1;0;"
    )
    assert reagent_dist.to_string() == expected_string

    worklist.add_record(reagent_dist)

    gwl_string = worklist.records_to_string()

    assert (
        gwl_string
        == "A;Source1;;4ti-0960/B on raised carrier;3;;50;;;;\nD;Destination;;"
        "4ti-0960/B on CPAC;1;;50;;;;\nW2;\nW;\nWD;\nF;\nB;\nS;diti_index\nC;"
        "Multiline\\ncomment\nR;SrcRackLabel;SrcRackID;SrcRackType;SrcPosStart;"
        "SrcPosEnd;DestRackLabel;DestRackID;DestRackType;DestPosStart;DestPosEnd;"
        "Volume;;1;1;0;\n"
    )

    target_gwl = os.path.join(str(tmpdir), "test.gwl")
    worklist.records_to_file(target_gwl)

    with open(target_gwl, "a") as f:
        f.write("XYZ;appended text")  # testing invalid records

    with pytest.raises(ValueError):
        dioscuri.read_gwl(target_gwl)
